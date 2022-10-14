# Ad Inventory Fraud Measurement

This repository is associated with the measurement study based research titled "**The Inventory is Dark and Full of Misinformation:
Understanding the Abuse of Ad Inventory Pooling in the Ad-Tech Supply Chain**". In this work, for the first time, we study and measure different mechanisms employed in the ad-tech ecosystem to misrepresent the ad inventory in order to fraud the advertisers. We perform our study on a set of 669 misinformation websites as they are more prone to engage in this kind of ad fraud so as to deceive brands in monetizing their misinformative websites. However, this repository contains the template code to repeat the work done in our research for any set of websites. 

The dataset associated with our work can be accessed below. It can be used to reproduce the results detailed in our paper.\
**Dataset:** [OSF Project Repository](https://osf.io/hxfkw/?view_only=bda006ebbd7d4ec2be869cbb198c6bd5)  

For further details, please check out the research paper associated with this work.\
**Paper:** https://doi.org/10.48550/arXiv.2210.06654

We study Ad Inventory Fraud in three ways:
1. ads.txt misrepresentations
2. sellers.json misrepresentations
3. Dark Pooling

It is recommended to follow the same directory structure as used in the repository to avoid an errors. Primarily, all the Python dependencies required to run this project can be installed using the following command:
```
pip install -r requirements.txt
```

## ads.txt misrepresentations

The ads.txt standard (introduced in 2017) aims to address ad slot inventory fraud by requiring each publisher domain to maintain an ads.txt file
at the root level directory (e.g., publisher.com/ads.txt). The ads.txt file should contain entries for all ad exchanges that are authorized to sell or resell the ad inventory of the publisher. Our work is based on [2021 IAB Specification](https://iabtechlab.com/wp-content/uploads/2021/03/ads.txt-1.0.3.pdf) for ads.txt. (**Note**: "ads" in "ads.txt" stands for `Authorized Digital Sellers`.)

The following scenarios describe different misrepresentations in ads.txt:

<p align="center">
  <img src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9781761/adstxt-inventory-fraud-toy-examples.pdf">
</p>

In order to study these ads.txt misrepresentations, first step is to crawl ads.txt using the codes present in `ads.txt-crawler` directory.

1. Enter the list of _valid_ websites in the file `websites_to_crawl.txt` by adding each website on a new line.
2. Download the appropriate version of chrome webdriver corresponding to the current version of your chrome browser and OS from the following link:
   https://chromedriver.chromium.org/downloads 
3. Replace the executable `chromedriver` inside the `ads.txt-crawler` directory with the executable obtained by unzipping the downloaded file in Step 2.
4. Run ads.txt crawler using the following command to download ads.txt for your websites (wherever available). ads.txt will be downloaded in `ads.txt-crawler/adstxt` directory. The subset of websites for whom ads.txt was _not_ found are associated with "No" in the `adstxt_presence.txt` file:
   ```
   python crawl_adstxt.py
   ```
5. Next, the downloaded ads.txt files can be parsed and pre-processed to eliminate irrelevant text by running the following command. It will generate a unified summary file `summary_adstxt.csv` containing entries of all the ads.txt files downloaded in Step 4.
   ```
   python parse_adstxt.py
   ```
6. Finally, `xxx.py` can be ran as follows to obtain all the different types of ads.txt misrepresentations described in the figure above.
   ```
   python xxx.py
   ```


## sellers.json misrepresentations

The sellers.json standard (introduced in 2019), aims to mitigate inventory fraud by requiring each AdX and SSP to maintain a sellers.json file at the root level directory (e.g., adx.com/sellers.json). This sellers.json file must contain an entry for each entity that may be paid for inventory purchased through an AdX — i.e., one entry for each partner that is an inventory source for the AdX. Our work is based on [2019 IAB Specification](https://iabtechlab.com/wp-content/uploads/2019/07/Sellers.json_Final.pdf) for sellers.json.

The following scenarios describe different misrepresentations in ads.txt:

<p align="center">
  <img src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9781965/sellersjson-inventory-fraud.pdf">
</p>

In order to study sellers.json misrepresentations, first step is to crawl sellers.json using the codes present in `sellers.json-crawler` directory.

1. 


### Citation

If you find this work useful, please cite our research paper:

```
@misc{https://doi.org/10.48550/arxiv.2210.06654,
  doi = {10.48550/ARXIV.2210.06654},
  
  url = {https://arxiv.org/abs/2210.06654},
  
  author = {Vekaria, Yash and Nithyanand, Rishab and Shafiq, Zubair},
  
  keywords = {Cryptography and Security (cs.CR), Computers and Society (cs.CY), Networking and Internet Architecture (cs.NI), Social and Information Networks (cs.SI), FOS: Computer and information sciences, FOS: Computer and information sciences},
  
  title = {The Inventory is Dark and Full of Misinformation: Understanding the Abuse of Ad Inventory Pooling in the Ad-Tech Supply Chain},
  
  publisher = {arXiv},
  
  year = {2022},
  
  copyright = {Creative Commons Attribution 4.0 International}
}
```
