import ast
import json
import os.path
import pandas as pd 



def get_sellersjson_presence_mapping(sellersjson_presence_filepath):
    '''
    Reads sellersjson_presence.txt file and return a dict containing the mapping of ad domain to its sellers.json presence
    '''
    ad_domains = []
    sellersjson_presence_mapping = {}
    # Each line represents a seller and its sellers.json presence information (Yes/No) separated by a comma
    with open(sellersjson_presence_filepath, "r") as f:
        lines = f.read().split("\n")
        for line in lines:
            temp = line.split(", ")
            if temp[0] not in ad_domains:
                ad_domains.append(temp[0])
            sellersjson_presence_mapping[temp[0]] = temp[1]
    f.close()

    return ad_domains, sellersjson_presence_mapping



def parse_sellersjson(sellersjson_presence_filepath, outpath_filepath, sellersjson_directory):

    dataframe = []
    # Obtain all distinct domains already observed/crawled and sellers.json presence for them
    domains, sellerjson_presence_dict = get_sellersjson_presence_mapping(sellersjson_presence_filepath)

    # Open a file to save the list of failed sellers
    fs = open(sellersjson_presence_filepath.replace("sellersjson_presence","failed_sellers"),"a")

    for site in sorted(domains)[:]:
        print(sorted(domains).index(site), site)

        # matchthememory has junk sellers.json, so it is ignored
        if site in ["matchthememory.com"]:
            sellerjson_presence_dict[site] = "No"
        
        # Generate filename from the website
        filename = site.replace(".","_") + ".json"
        fpath = os.path.join(sellersjson_directory, filename)
        
        # Parse sellers.json only if it has one
        if sellerjson_presence_dict[site] == "Yes":
        # if os.path.isfile(fpath):
            if "google.com" in site:
                site = "google.com"
                fpath = sellersjson_directory + site.replace(".","_") + ".json"
            elif "inmobi.com" in site:
                site = "inmobi.com"
            elif "rubiconproject.com" in site:
                site = "rubiconproject.com"
            elif "video.unrulymedia.com" in site:
                site = "video.unrulymedia.com"

            f = open(fpath)
            ad_sellers = {}
            json_string = ""

            # google.com's sellers.json is parsed in a different way due to some characters.
            try:
                if site in ["google.com"]:
                    ad_sellers = json.loads(ast.literal_eval(json.dumps(f.read())))
                else:
                    json_string = json.load(f)
                    ad_sellers = json.loads(json_string)
            except json.JSONDecodeError as e:
                try:
                    if json_string != "":
                        # Correcting some incorrect syntax of JSON
                        json_string.replace(" ","").replace("\n","").replace("\t","").replace(",]","]").replace(",}","}").strip(",")
                        ad_sellers = json.loads(json_string)
                except:
                    # If syntax of the JSON could not be correct, it is regarded as failed and written to the file
                    f.close()
                    fs.write(filename)
                    fs.write("\n")
                    item_list = []
                    item_list.append(site)
                    item_list.append("Yes")
                    item_list.append(-1)
                    item_list.append("NA")
                    item_list.append("NA")
                    item_list.append("NA")
                    item_list.append("NA")
                    item_list.append("NA")
                    
                    dataframe.append(item_list)
                    print(sorted(domains).index(site), item_list)
                    continue

            try:
                ad_domain = str(site).replace("https://","").replace("http://","").replace("www.","")
                ad_domain = str(ad_domain.strip().strip("/").strip(".").replace("/en/home","").replace("/en","").replace("/es","").replace("wwwmicro","www.micro").replace("/sellers.json","").replace("com.decenterads.ron","decenterads.com").replace("/push/spanish","").replace(" (Inherited: obox.com )", "").replace(" ","").replace("www.transmit.live","cdn.transmit.live").replace("com.originmedia.ron","originmedia.com").replace("corp.meitu.com","www.meitu.com").replace("www.stnvideo.com","cache.sendtonews.com").replace("com.vrtcal.ron","vrtcal.com").replace("com.vidillion.ron","vidillion.com").replace("/info","").replace("https://","").replace("http://","").replace("www.","").lower())
                sellerjson_presence = "Yes"
                seller_count = len(ad_sellers["sellers"])
            except:
                fs.write(filename)
                fs.write("\n")
                item_list = []
                item_list.append(site)
                item_list.append("Yes")
                item_list.append(-1)
                item_list.append("NA")
                item_list.append("NA")
                item_list.append("NA")
                item_list.append("NA")
                item_list.append("NA")
                
                dataframe.append(item_list)
                print(sorted(domains).index(site), item_list)
                continue

            for seller in ad_sellers["sellers"]:
                item_list = []
                seller_id = "NA"
                is_confidential = "False"
                seller_type = "NA"
                seller_name = "NA"
                seller_domain = "NA"

                # Obtain seller_id of current seller
                if "seller_id" in seller.keys():
                    seller_id = seller["seller_id"]

                # epom.com/sellers.json
                if "sellerId" in seller.keys():
                    seller_id = seller["sellerId"]

                # wurl.com/sellers.json
                if "id" in seller.keys():
                    seller_id = seller["id"]
                
                # Obtain if the current seller is_confidential
                if "is_confidential" in seller.keys():
                    if seller["is_confidential"] == 1:
                        is_confidential = "True"

                # Obtain seller_type of current seller
                if "seller_type" in seller.keys():
                    seller_type = str(seller["seller_type"]).upper()

                # Obtain name of the current seller
                if "name" in seller.keys():
                    seller_name = seller["name"]

                # epom.com/sellers.json
                if "developer" in seller.keys():
                    seller_name = seller["developer"]

                # Obtain seller_id of current seller
                if "domain" in seller.keys():
                    seller_domain = str(seller["domain"]).replace("https://","").replace("http://","").replace("www.","").lower()

                # epom.com/sellers.json
                if "website" in seller.keys():
                    seller_domain = str(seller["website"]).replace("https://","").replace("http://","").replace("www.","").lower()
                
                # Append the details about the current seller to the dataframe
                item_list.append(ad_domain)
                item_list.append(sellerjson_presence)
                item_list.append(seller_count)
                item_list.append(seller_id)
                item_list.append(is_confidential)
                item_list.append(seller_type)
                item_list.append(seller_name)
                item_list.append(seller_domain)

                dataframe.append(item_list)
                print(sorted(domains).index(site), item_list)

            f.close()
        else:
            if "google.com" in site:
                site = "google.com"
            site = str(site).replace("https://","").replace("http://","").replace("www.","")
            site = str(site.strip().strip("/").strip(".").replace("/en/home","").replace("/en","").replace("/es","").replace("wwwmicro","www.micro").replace("/sellers.json","").replace("com.decenterads.ron","decenterads.com").replace("/push/spanish","").replace(" (Inherited: obox.com )", "").replace(" ","").replace("www.transmit.live","cdn.transmit.live").replace("com.originmedia.ron","originmedia.com").replace("corp.meitu.com","www.meitu.com").replace("www.stnvideo.com","cache.sendtonews.com").replace("com.vrtcal.ron","vrtcal.com").replace("com.vidillion.ron","vidillion.com").replace("/info","").replace("https://","").replace("http://","").replace("www.","").lower())

            item_list = []
            item_list.append(site)
            item_list.append("No")
            item_list.append(-1)
            item_list.append("NA")
            item_list.append("NA")
            item_list.append("NA")
            item_list.append("NA")
            item_list.append("NA")
            
            dataframe.append(item_list)
            print(sorted(domains).index(site), item_list)

    fs.close()
    # Write the parsed details of the seller into the summary_sellersjson.csv file
    header = ["ad_domain", "sellerjson_presence", "seller_count", "seller_id", "seller_is_confidential", "seller_type", "seller_name", "seller_domain"]
    df = pd.DataFrame(dataframe, columns=header)
    df.to_csv(outpath_filepath, index=False)

    return



def main():

    # Enter the path to the file to store output about the presence of the sellers.json
    sellersjson_presence_directory, sellersjson_presence_filename = "", "sellersjson_presence.txt"
    sellersjson_presence_filepath = os.path.join(sellersjson_presence_directory, sellersjson_presence_filename)

    # Define path to store the sellers.json summary file
    output_directory, output_filename = "", "summary_sellersjson.csv"
    outpath_filepath = os.path.join(output_directory, output_filename)
    
    # Define directory containing the crawled sellers.json files
    sellersjson_directory = "./sellersjson/"

    # Parse the crawled sellers.json files and perform pre-processing
    parse_sellersjson(sellersjson_presence_filepath, outpath_filepath, sellersjson_directory)



if __name__ == "__main__":
    main()

