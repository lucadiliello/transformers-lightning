import torch

from transformers_lightning.metrics.retrieval.retrieval_metric import RetrievalMetric
from transformers_lightning.metrics.functional.hit_rate import hit_rate


class HitRateAtK(RetrievalMetric):
    r"""
    Computes `Hit Rate`.
    Works with binary data. Accepts integer or float predictions from a model output.

    Forward accepts
    - ``indexes`` (long tensor): ``(N, ...)``
    - ``preds`` (float tensor): ``(N, ...)``
    - ``target`` (long or bool tensor): ``(N, ...)``
    `indexes`, `preds` and `target` must have the same dimension.
    `indexes` indicate to which query a prediction belongs.

    Predictions will be first grouped by indexes and then HR will be computed as the mean
    of the HR over each query.

    Args:
        query_without_relevant_docs:
            Specify what to do with queries that do not have at least a positive target. Choose from:

            - ``'skip'``: skip those queries (default); if all queries are skipped, ``0.0`` is returned
            - ``'error'``: raise a ``ValueError``
            - ``'pos'``: score on those queries is counted as ``1.0``
            - ``'neg'``: score on those queries is counted as ``0.0``
        exclude:
            Do not take into account predictions where the target is equal to this value. default `-100`
        compute_on_step:
            Forward only calls ``update()`` and return None if this is set to False. default: True
        dist_sync_on_step:
            Synchronize metric state across processes at each ``forward()``
            before returning the value at the step. default: False
        process_group:
            Specify the process group on which synchronization is called. default: None (which selects
            the entire world)
        dist_sync_fn:
            Callback that performs the allgather operation on the metric state. When `None`, DDP
            will be used to perform the allgather. default: None

    Example:
        >>> indexes = torch.tensor([0, 0, 0, 1, 1, 1, 1])
        >>> preds = torch.tensor([0.2, 0.3, 0.5, 0.1, 0.3, 0.5, 0.2])
        >>> target = torch.tensor([False, False, True, False, True, False, False])
        >>> hr_k = HitRateAtK(k=1)
        >>> hr_k(indexes, preds, target)
        tensor(0.5)
        >>> hr_k.compute()
        tensor(0.5)
    """

    def __init__(self, *args, k: int = 1, **kwargs):
        super().__init__(*args, **kwargs)

        if not k or k <= 0:
            raise ValueError("`k` must be an integer greater than 0")

        self.k = k

    def _metric(self, preds: torch.Tensor, target: torch.Tensor) -> torch.Tensor:
        valid_indexes = target != self.exclude
        return hit_rate(preds[valid_indexes], target[valid_indexes], k=self.k)
