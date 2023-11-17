# example-plugin
An example of Poisson PDF implementation for Spey. This plug-in implements the following likelihood distribution:

$$
\mathcal{L}(\mu) = \prod_{i\in{\rm bins}}{\rm Poiss}(n^i|\mu n_s^i + n_b^i)
$$

where $n, n_s$ and $n_b$ are data, signal and background yields, respectively.

These files are designed to be implemented as a plug-in for the spey interface and can be used as a template. Please see [Spey's documentation](https://speysidehep.github.io/spey/) for details on implementing different features.

This plug-in can be installed from GitHub with `pip`

```
python -m pip install --upgrade "git+https://github.com/SpeysideHEP/example-plugin"
```

or from the locally cloned repository

```
python -m pip install --upgrade .
```

## Usage

Once this plug in is installed, the model can be used through Spey as follows
```python
stat_wrapper = spey.get_backend('example.poisson')
stat_model = stat_wrapper(
    signal_yields= np.array([12,15]),
    background_yields = np.array([50.,48.]),
    data=np.array([36,33])
)
```
Notice that the name of the accessor ``'example.poisson'`` is the same as in ``setup.py`` and the class' ``name`` attribute. The exclusion limit can be computed via the following command:
```python
print(stat_model.exclusion_confidence_level())
# [0.9999807105228611]
```
Thats it!
Have fun!
