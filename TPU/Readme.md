This is some boilerplate for training the Art Classification dataset on TPU. 

The original link is [here @ Kaggle](https://www.kaggle.com/ikarus777/best-artworks-of-all-time)

The dataset has been stratified by target and split 80/20. 

Any multilabels have been reduced to the first label.

If there are any issues with the google storage "gs" link, you can generate new ones from the Kaggle TPU version [here](https://www.kaggle.com/alexanderlav/tpu-bestartworksofalltime). 

To generate new gs links, try opening a new notebook from that Kaggle Dataset, and then: 
```
from kaggle_datasets import KaggleDatasets
GCS_DS_PATH = KaggleDatasets().get_gcs_path()
```
The easiest links to use are the "train2" and "test2" .tfrecord files (represented in this repository's notebook)

----------------------------------------------------------------

You may also need to connect your Google account (though shouldn't). Here's the boilerplate incase you need to do the search for how to do that:

```
from kaggle_secrets import UserSecretsClient
user_secrets = UserSecretsClient()
user_credential = user_secrets.get_gcloud_credential()
user_secrets.set_tensorflow_credential(user_credential)
```
