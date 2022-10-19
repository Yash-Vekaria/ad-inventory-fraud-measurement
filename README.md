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

The overall methodology followed in this work can be described as follows:

<p align="center">
  <img src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9822194/misinfo_model.pdf">
</p>


It is recommended to follow the same directory structure as used in the repository to avoid an errors. Primarily, all the Python dependencies required to run this project can be installed using the following command:
```
pip install -r requirements.txt
```

## ads.txt crawler

The ads.txt standard (introduced in 2017) aims to address ad slot inventory fraud by requiring each publisher domain to maintain an ads.txt file
at the root level directory (e.g., publisher.com/ads.txt). The ads.txt file should contain entries for all ad exchanges that are authorized to sell or resell the ad inventory of the publisher. Our work is based on [2021 IAB Specification](https://iabtechlab.com/wp-content/uploads/2021/03/ads.txt-1.0.3.pdf) for ads.txt. (**Note**: "ads" in "ads.txt" stands for `Authorized Digital Sellers`.)

In order to study these ads.txt misrepresentations, first step is to crawl ads.txt using the codes present in `ads.txt-crawler` directory.

1. Enter the list of _valid_ websites in the file `websites_to_crawl.txt` by adding each website on a new line.
2. Download the appropriate version of chrome webdriver corresponding to the current version of your chrome browser and OS from the following link and place it at the location as shown above.
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


## sellers.json crawler

The sellers.json standard (introduced in 2019), aims to mitigate inventory fraud by requiring each AdX and SSP to maintain a sellers.json file at the root level directory (e.g., adx.com/sellers.json). This sellers.json file must contain an entry for each entity that may be paid for inventory purchased through an AdX — i.e., one entry for each partner that is an inventory source for the AdX. Our work is based on [2019 IAB Specification](https://iabtechlab.com/wp-content/uploads/2019/07/Sellers.json_Final.pdf) for sellers.json.

In order to study sellers.json misrepresentations, first step is to crawl sellers.json using the codes present in `sellers.json-crawler` directory. This is the most expensive crawler in terms of the amount of time it takes.

1. Considering that `ads.txt-crawler` was already set first and ran, `chromedriver` will be directly used from the path as per the above directory structure. Also, `crawl_sellersjson_recursively.py` (to be run as below) crawls sellers.json for all the distinct ad domains found in the `summary_adstxt.csv` during the first iteration. The crawler maintains a mapping of sellers to the presence of their sellers.json file in `sellersjson_presence.txt`. 
   ```
   python crawl_sellersjson_recursively.py
   ```
2. After each iteration, a summarized file is created for all the sellers.json files crawled until that point using the `parse_sellersjson.py` code internally called by `crawl_sellersjson_recursively.py`.
3. For second iteration onwards, all the seller domains with `seller_type` as {"_INTERMEDIARY_" or "_BOTH_"} that are extracted from `summary_sellersjson.csv` and uncrawled, are crawled anew.
4. Steps 2 and 3 are repeated for 5 iterations expecting that sellers.json of all possible sellers would have been crawled. `summary_sellersjson.csv` obtained after all 5 iterations contains entries for all the sellers.json files crawled in these 5 iterations.
5. If any unexpected failure happens at any iteration, then the crawl can be restarted from that iteration by changing the line `range(1, 6)` in `crawl_sellersjson_recursively.py` to `range(x, 6)`, where x is the iteration in which the failure occured.

**Note**: 
* _Best effort crawling attempt is made using the above codes. However, there could be instances where the crawled sellers.json is syntactically incorrect and has may fail being parsed by our code. All such sellers.json filenames which are downloaded but have incorrect JSON format are saved in the file `failed_sellers.txt`._ These files can be opened to manually correct the  syntactical sellers.json formatting and the above steps can be rerun.
* _Google has an extremely large number of sellers (5M+) in its sellers.json file, which is also hosted on a non-standard location: http://realtimebidding.google.com. So, its presence is hard-coded to "Yes" and the link has been opened on Safari to manually copy paste its entire content in `google_com.json` named file._


## Discovering misrepresentations

The following scenarios describe different misrepresentations in `ads.txt` file:

<p align="center">
  <img src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9793766/adstxt-inventory-fraud-toy-examples.pdf">
</p>

The following scenarios describe different misrepresentations in `sellers.json` file:

<p align="center">
  <img src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9793769/sellersjson-inventory-fraud.pdf">
</p>

The counts for above misrepresentations can be discovered in ads.txt and sellers.json files using the `summary_adstxt.csv` and `summary_sellersjson.csv` files respectively generated above. 

The following commands need to be run inside `Misrepresentations` directory:
1. **ads.txt misrepresentations**: Output file: `adstxt_misrepresentations.csv`
   `discover_adstxt_misrepresentations.py` has been parallelized using Python `multiprocessing` library because usually even for 5 websites, the `summary_sellersjson.csv` becomes very large and non-parallel processing can take more time. `chunksize` representing the number of websites to be assigned to each thread and `agents` representing the number of threads to be run in parallel are initialized inside the `main()` function. These should be customized as per the number of websites studied by you.
   ```
   python discover_adstxt_misrepresentations.py
   ``` 
2. **sellers.json misrepresentations**: Output file: `sellersjson_misrepresentations.csv`
   ```
   python discover_sellersjson_misrepresentations.py
   ```


## Discovering Pooling

Pooling is a common strategy to share resources in online advertising. One way to identify the occurrence of pooling is by noting a single AdX-issued ‘publisher ID’ shared by multiple publisher websites. Dark pools are pools in which publisher IDs are shared by organizationally-unrelated publishers (possibly of different reputations). Dark pooling is a kind of ad fraud where advertisers are deceived during real-time bidding to think that they are buying an ad inventory on a premium website for instance, while their ad ends-up being shown on a low-end website due to a collusion between the premium and the low-end publisher in this case. Pooling can be studied statically as well as dynamically when websites are visited in real-time. The following diagram shows different kind scenarios related to Pooling.

<p align="center">
  <img src="https://github.com/Yash-Vekaria/Ad-Inventory-Fraud-Measurement/files/9822175/dark-pooling.pdf">
</p>

In order to study whether the websites under the study are involved in pooling, there should be a broader list of websites with whom they might share seller Ids. As a result, the Top 100K Tranco websites are used here, with the intuition that any website under study might want to pool their inventory with a reputable website. If required, any custom set of websites could be used instead of Top 100K.

The Top 100K Tranco websites are extracted from the Top 1M Tranco websites available at `https://tranco-list.eu/list/25749/1000000` and accesssed on 15th October 2022. 
3. Top 100K domains are pasted from this list in `top_100k_websites.txt` and `ads.txt-crawler` is ran on these Top 100K domains to download their ads.txt files (wherever available) in the directory `./ads.txt-crawler/adstxt_top100k/` To run `ads.txt-crawler` for Top 100K domains, comment and uncomment the following lines in `crawl_adstxt.py`. It is recommended to download and use the latest tranco ranked list of domains whenever performing this study by updating the `top_100k_websites.txt` file and re-crawling their ads.txt files. 
1. Lines to comment in `crawl_adstxt.py`:
   ```
   input_directory, input_filename = "..", "websites_to_crawl.txt"
   adstxt_presence_directory, adstxt_presence_filename = "", "adstxt_presence.txt"
   output_directory = "./adstxt/"
   ```
2. Lines to uncomment in `crawl_adstxt.py`:
   ```
   input_directory, input_filename = "..", "top_100k_websites.txt"
   adstxt_presence_directory, adstxt_presence_filename = "", "top100k_adstxt_presence.txt"
   output_directory = "./adstxt_top100k/"
   ```

### Static Pooling

Static Pooling involves studying the signs of collusion by analysing the static files of `ads.txt` of study websites and the Top 100K websites and the set of and `sellers.json` files. Follow the steps below:

1. In order to obtain the parent organization of each domain under our study as well as for the Top 100K tranco domains, Entity-Organization List provided by DuckDuckGo (DDG) in their `tracker-radar` repository is used. Since, this repository is huge, it is recommended to clone it in a temporary folder using the following command.
   ```
   git clone https://github.com/duckduckgo/tracker-radar.git
   ```
2. Once, cloning completes, cut the folder titled `entities` from the cloned repository and paste it inside the `Pooling` directory of the current project's folder. `entities` is referenced from this location by the `discover_static_pools.py` script. If it is placed at some other location, remember to change the location at the global variables defined in this script. The temporary folder can be deleted.
3. Now, the following command can be run to generate a file named `static_pools.csv` inside the `Pooling` directory. It contains all the pools discovered from the ads.txt files of study websites as well as Top 100K websites where more than 1 websites share the same seller Id. More details about this file can be obtained from our Dataset page.
   ```
   python discover_static_pools.py
   ```

### Dynamic Pooling

Dynamic Pooling involves studying the signs of collusion between two or more websites (i.e., existence of static pools) by actually visiting the websites under study in real-time, capturing all the bid request, responses and post data and analysing them to find the evidence of such a collusion. We collect this data as explained in the Methodology diagram above. The codes are present in `/Pooling/dynamic-crawler/`. To perform dynamic crawls of a website perform the following steps:

1. `browsermobproxy` is used to download HAR files containing all requests, responses and post data while visiting the website. We used `browsermob-proxy-2.1.4`. However, you can use another latest version by putting its folder here and changing the path accordingly in the files: `dynamic_crawl.py` and `Dockerfile`.
2. `webdriver_utils.py` and `XPathUtil.py` are some dependent codes used by `dynamic_crawl.py`.
3. Crawling a single website can variably take few minutes to a couple of hours. So, `docker` is used to spawn independent containers in order to parallelise crawls. This parallelisation is achieved by the code `multi_run.py`.
4. `Dockerfile` spawns an image that downloads and install the latest stable version of google chrome. However, chromerdriver is downloaded based on the version provided. At the time of experimentation, the lastest google chrome version was v106 so chromedriver download URL corresponding to that version was used. However, while running the code, if it changes, visit https://chromedriver.chromium.org/downloads and select appropriate latest chrome version. From the resulting download page _copy link_ for `chromedriver_linux64.zip` and replace the existing link in `Dockerfile`.
5. `filterlists` are used to classify whether a URL is ad or non-ad. If you wish to use latest filterlist rules, delete this folder from your local repository and then when `dynamic_crawl.py` shall be run, these lists will be auto-downloaded. 
6. Next, paste the websites to crawl in the file `study_websites.txt`, with each website on a new line and in a valid format (e.g. preceding with `http://`).
7. It is recommended to be familiar with the dockers. However, if not, the beginning portion of `multi_run.py` contains some useful commands. First donwload and install `docker` from https://docs.docker.com/engine/install/ based on your system specifications.
8. Based on the number of websites input in `study_websites.txt` decide number of threads (i.e., docker containers) to spawn by changing the value of variable: `NUM_THREADS` in `multi_run.py`. In the same file also change the variable `crawl_number` to either a string representing current crawl or a number identifying the count of crawl being performed. A foldername with this input preceded by string `crawl_` will be created to contain different output files for each website.
9. Now, first the docker image should be built using the following command:
   ```
   docker build -t dynamic-crawler .
   ```
   Here, `dynamic-crawler` is the image name, it can be replaced by any custom name of choice. It will take some time and memory to build the docker. While its being built, you will see any issues/errors if they exist and the build will stop. Correct these issues and rerun the above command until its built successfully.
10. Next, simply spawn the dockers and begin the dynamic crawl by running the following command:
    ```
    python multi_run.py
    ```
11. Keep monitoring the docker containers spawned for a few minutes to catch and correct and runtime issues. Run the following command to view all active and inactive dockers:
    ```
    docker container ls -a
    ```
   Docker containers that are exited too soon are probably problematic, the log of runtime errors can be seen for by running the following for a container id obtainer from the above command.
    ```
    docker container logs -f e1cbe52763d5
    ```
12. Once the issue is fixed in the code, first delete all the previous docker containers with the following command and then repeat the steps from 9-11 until all the websites are successfully crawled:
    ```
    docker rm -f $(docker ps -a -q)
    ```
13. The folder `crawl_<crawl_number>` will contain a separate output folder for each website. Each website folder contains the following output files generated by `dynamic_crawl.py`. The filenames below are shown for `breitbart.com` as collected on `18th Oct 2022`:
  * `<crawl_number>|har|breitbart_com|18_10_2022.har`: HAR file containing all HTTP requests, responses and post data. 
  * `<crawl_number>|hb|breitbart_com|18_10_2022.json`: JSON file containing Header Bidding (HB) data from `prebid.js`. 
  * `<crawl_number>|ss|breitbart_com|18_10_2022.png`: PNG file capturing the screenshot of the entire webpage of the visited sites. This is stored to view the ads shown on breitbart. 
  * `<crawl_number>|brand|breitbart_com|18_10_2022.txt`: TXT file containing list of `{<ad_exchange>, <brand>}` pairs for each brand observed to advertise. 
  * `<crawl_number>|mapping|breitbart_com|18_10_2022.txt`: TXT file containing the same entries as above file, but it also has the URL of ad exchange that led to the brand page.
  * `<crawl_number>|error|breitbart_com|18_10_2022.txt`: TXT file logging all the minor exceptions that occured while performing the crawl for that website.



## Discovering Brands

Brands advertising on the set of websites being studied have already been obtained during the dynamic crawling performed above. The following code (located in `/Advertisers`) can be run to summarise and obtain a list of all the advertisers on each study website. 
    ```
    python collect_brands.py
    ```
Input the list of folders of the dynamic crawls (generated in in `/Pooling/dynamic-crawler/`) that you want to summarise in the variable: `crawls_to_summarise`. The output is stored in the file `brands.csv` containing `{<study_website>, <brand>}` pairs.


***

**For any issues pertaining to this repository, please raise a Pull Request (PR). For any additional questions related to this research, feel free to reach out to `yvekaria@ucdavis.edu`.**

***


## Citation

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
