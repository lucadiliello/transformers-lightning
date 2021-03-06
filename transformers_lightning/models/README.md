# Models

This package containts two high-level models that can be used to inherit some useful methods and a general standardized structure.


## TransfomersModel

`TransformersModel` only overrides `configure_optimizers` by returning a better optimizer and the relative scheduler and finally provides a `add_model_specific_args` to automatically add the parameters of the optimizer to the global parser.

Example:
```python
>>> parser = TransformerModel.add_model_specific_args(parser)
>>> save_transformers_callback = callbacks.TransformersModelCheckpointCallback(hparams)
>>> hparams = parser.parse_args()
```
