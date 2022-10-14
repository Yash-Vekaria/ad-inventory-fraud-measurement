import os
import pandas as pd



def read_website_list(filepath):
    '''
    Reads and Returns websites under study from the file locations passed to it
    '''
    sites = []
    with open(filepath, "r") as f:
        sites = f.read().split("\n")
    f.close()
    return sites



def read_adstxt(adstxt_directory, filename):
    '''
    Reads and Returns all the entries of ads.txt file
    '''
    filepath = adstxt_directory + filename
    f = open(filepath, "r")
    ad_sellers = f.read().split("\n")
    f.close()
    
    return ad_sellers



def get_adstxt_presence_mapping(adstxt_presence_filepath):
    '''
    Reads adstxt_presence.txt file and return a dict containing the mapping of website to its ads.txt presence
    '''
    adstxt_presence_mapping = {}
    with open(adstxt_presence_filepath, "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            temp = line.split(", ")
            adstxt_presence_mapping[temp[0]] = temp[1]
    f.close()

    return adstxt_presence_mapping



def parse_adstxt(websites, adstxt_directory, adstxt_presence_dict):

    # Initializing an empty list to save all the pre-processed ads.txt entries
    dataframe = []
    
    for site in websites:

        # Obtain the filename in the same way as it was generated in the crawl_adsxt.py file
        filename = site.replace("https://","").replace("http://","").replace("www.","").replace(".","_") + ".txt"
        
        # Open and pre-process ads.txt file of a website if it has one
        if adstxt_presence_dict[site] == "Yes":
            
            # Obtain ads.txt entries
            adstxt_entries = read_adstxt(adstxt_directory, filename)

            for seller in adstxt_entries:
                
                # item_list stores different information about a seller
                item_list = []
                s = seller
                
                # Character "#" is used to denote comment in ads.txt. So, text after "#" is ignored
                if "#" in seller:
                    s = seller[:seller.index("#")]

                # Ignoring garbage which is too short to represent any valid seller
                if len(s) < 5:
                    continue
                else:
                    # Append current website and ads.txt presence
                    item_list.append(site)
                    item_list.append(adstxt_presence_dict[site])
                    
                    # Obtain different components of an ads.txt entry (which are separated by a ",")
                    temp = s.split(",")
                    
                    # Strip any empty spaces in front and last and convert current "ad_domain" to lower case
                    item_list.append(temp[0].strip().lower())
                    
                    if len(temp) >= 2:
                        if temp[1].strip() == "":
                            item_list.append("NA")
                        else:
                            # Extract and append current "seller id"
                            item_list.append(temp[1].strip())

                        if len(temp) >= 3:
                            if temp[2].strip() == "":
                                item_list.append("NA")
                            else:
                                # Extract and append current "seller_account_type"
                                item_list.append(temp[2].strip().upper())

                            if len(temp) >= 4:
                                if temp[3].strip() == "":
                                    item_list.append("NA")
                                else:
                                    # Extract and append current "certification_authority_id"
                                    item_list.append(temp[3].strip())
                            else:
                                item_list.append("NA")
                        else:
                            item_list.append("NA")
                            item_list.append("NA")
                    else:
                        item_list.append("NA")
                        item_list.append("NA")
                        item_list.append("NA")
                    
                    dataframe.append(item_list)
                    print(websites.index(site), item_list)	
            item_list = []
        else:
            # NA is appended for different seller components for the site without ads.txt
            item_list.append(site)
            item_list.append(adstxt_presence_dict[site])
            item_list.append("NA")
            item_list.append("NA")
            item_list.append("NA")
            item_list.append("NA")

        # Append current seller details to the dataframe
        if item_list:
            dataframe.append(item_list)
            print(websites.index(site), item_list)
        else:
            continue

    return dataframe



def generate_adstxt_summary(dataframe, outpath_filepath):
    header = ["website_domain", "adstxt_presence", "ad_domain", "seller id", "seller_account_type", "certification_authority_id"]
    df = pd.DataFrame(dataframe, columns=header)
    df.to_csv(outpath_filepath, index=False)



def main():

    # Define path to list of websites that are under study
    input_directory, input_filename = "..", "websites_to_crawl.txt"
    input_filepath = os.path.join(input_directory, input_filename)

    # Enter the path to the file to store output about the presence of the ads.txt
    adstxt_presence_directory, adstxt_presence_filename = "", "adstxt_presence.txt"
    adstxt_presence_filepath = os.path.join(adstxt_presence_directory, adstxt_presence_filename)

    # Define path to store the ads.txt summary file
    output_directory, output_filename = "", "summary_adstxt.csv"
    outpath_filepath = os.path.join(output_directory, output_filename)
    
    # Define directory containing the crawled ads.txt files
    adstxt_directory = "./adstxt/"

    # Read list of websites under the study and mapping about their ads.txt presence
    crawled_websites = read_website_list(input_filepath)
    adstxt_presence_dict = get_adstxt_presence_mapping(adstxt_presence_filepath)

    # Parse the crawled ads.txt files and perform pre-processing
    summary_df = parse_adstxt(crawled_websites, adstxt_directory, adstxt_presence_dict)

    # Generate a summary csv file containing entries from all crawled ads.txt files after pre-processing
    generate_adstxt_summary(summary_df, outpath_filepath)



if __name__ == "__main__":
    main()

