import os
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options



def get_chromedriver():
    '''
    Returns an instance of chromedriver
    '''
    # Download appropriate chromedriver from: https://chromedriver.chromium.org/downloads based on your chrome browser version
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path="../chromedriver", options=chrome_options)
    driver.set_page_load_timeout(10)
    return driver


def read_websites_to_crawl(filepath):
    '''
    Reads and Returns websites from the file locations passed to it
    '''
    sites = []
    with open(filepath, "r") as f:
        sites = f.read().split("\n")
    f.close()
    return sites



def crawl_adstxt(websites, driver, output_directory, adstxt_presence_filepath):
    
    fm = open(adstxt_presence_filepath, "w")

    for site in websites:

        termination_char = ""
        if websites.index(site) != len(websites)-1:
            termination_char = "\n"

        # Check for ads.txt presence at the root level of a website
        site_adstxt_location = str(site) + "/ads.txt"
        if "http" not in site_adstxt_location:
            site_adstxt_location = "http://" + site_adstxt_location
        
        try:
            # Open the ads.txt file for the current website
            driver.get(site_adstxt_location)
        except:
            # Store ads.txt presence in a file
            fm.write(str(site) + f", No{termination_char}")
            print(site, "Failed!!")
            continue
        
        # Crawl the content of the ads.txt file using BeautifulSoup
        html_str = driver.page_source
        soup = BeautifulSoup(html_str, features="html.parser")
        str_content = soup.get_text()

        # Ads.txt file has entries which are either DIRECT or RESELLER type. So, check the ads.txt content for these types of entries
        if (("DIRECT" in str_content) or ("direct" in str_content) or ("Direct" in str_content)) or (("RESELLER" in str_content) or ("reseller" in str_content) or ("Reseller" in str_content)):
            output_filename = site.replace("https://","").replace("http://","").replace("www.","").replace(".","_") + ".txt"
            output_filepath = os.path.join(output_directory, output_filename)
            save_adstxt(output_filepath, str_content)
            fm.write(str(site) + f", Yes{termination_char}")
            print(site, "Crawled!")
        else:
            fm.write(str(site) + f", No{termination_char}")
            print(site, "Failed!!")     

    driver.quit()
    fm.close()

    return



def save_adstxt(filepath, content):
    '''
    Saves the content of ads.txt inside the file location passed to it
    '''
    f = open(filepath, 'w')
    f.write(content)
    f.close()



def main():

    # Define path to list of websites to crawl
    # input_directory, input_filename = "..", "websites_to_crawl.txt"
    input_directory, input_filename = "..", "top_100k_websites.txt"
    input_filepath = os.path.join(input_directory, input_filename)

    # Enter the path to the file to store output about the presence of the ads.txt
    # adstxt_presence_directory, adstxt_presence_filename = "", "adstxt_presence.txt"
    adstxt_presence_directory, adstxt_presence_filename = "", "top100k_adstxt_presence.txt"
    # adstxt_presence_directory, adstxt_presence_filename = "", "temp.txt"
    adstxt_presence_filepath = os.path.join(adstxt_presence_directory, adstxt_presence_filename)

    # Define path to output directory
    # output_directory = "./adstxt/"
    output_directory = "./adstxt_top100k/"
    
    # Read list of websites to crawl
    sites_to_crawl = read_websites_to_crawl(input_filepath)
    sites_to_crawl = sites_to_crawl[:70000]
    # sites_to_crawl = sites_to_crawl[70000:]
    fc = open("crawled.txt")
    temp = fc.read().split("\n")
    crawled = [dom.split(", ")[0].strip() for dom in temp]
    sites_to_crawl = list(set(sites_to_crawl).difference(set(crawled)))

    # Instantiate chromedriver
    web_driver = get_chromedriver()

    # Crawl ads.txt for the website list
    crawl_adstxt(sites_to_crawl, web_driver, output_directory, adstxt_presence_filepath)



if __name__ == "__main__":
    main()