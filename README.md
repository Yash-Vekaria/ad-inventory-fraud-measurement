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

The following scenarios describe correct representations and corresponding misrepresentations in ads.txt:

<p align="center">
  <img width="700" height="900" src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9781761/adstxt-inventory-fraud-toy-examples.pdf">
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
5. Next, the downloaded ads.txt can be parsed to eliminate irrelevant text by running the following command. It will generate a unified summary file `summary_adstxt.csv` containing entries of all the ads.txt files downloaded in Step 4.
6. Finally, `xxx.py` can be ran as follows to obtain all the different types of ads.txt misrepresentations described in the figure above.
   ```
   python xxx.py
   ```


## sellers.json misrepresentations

In order to study sellers.json misrepresentations, first step is to crawl ads.txt using the codes present in `ads.txt-crawler` directory.


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
