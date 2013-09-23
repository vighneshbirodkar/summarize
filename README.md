summarize
=========

A Python Library intended fo Automatic Text Summarization

# Development

```python
sudo python setup.py develop
```

#Example 
```python
from summarize import Document,DocumentSet

dset = DocumentSet('iphone')

words = dset.terms()
dset.docs()[0].visualize()
```
