from selenium.webdriver.common.action_chains import ActionChains
from requests.packages.urllib3.util.retry import Retry
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from requests.adapters import HTTPAdapter
from selenium.common.exceptions import (
	NoSuchElementException,
	InvalidSessionIdException,
	TimeoutException,
	WebDriverException,
	JavascriptException
)
from webdriver_utils import scroll_down
# from pyvirtualdisplay import Display
from adblockparser import AdblockRules
from selenium.webdriver import Chrome
from argparse import ArgumentParser
from browsermobproxy import Server
from selenium import webdriver
import datetime
from tld import get_fld
from time import sleep
from PIL import Image
import requests
import random
import math
import json
import tld
import os



# Uncomment and use the code lines below in order to access/debug chrome instrumentation remotely while running in non-headless mode
# Also uncomment the associated commented import
'''
disp = Display(backend="xvnc", size=(1920,1080), rfbport=1212) # XXXX has to be a random port number
disp.start()
'''

# Defining experimental options to chromer webdriver instate while instrumenting it
chrome_options = Options()
# chrome_options.binary_location = "/usr/bin/google-chrome-stable"
chrome_options.add_argument("--headless")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument('--ignore-ssl-errors=yes')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument("--window-size=1280,720")
global_curr_domain = ""



def download_lists(FILTERLIST_DIR):
	"""
	Function to download the lists used in AdGraph.
	Args:
		FILTERLIST_DIR: Path of the output directory to which filter lists should be written.
	Returns:
		Nothing, writes the lists to a directory.
	This functions does the following:
	1. Sends HTTP requests for the lists used in AdGraph.
	2. Writes to an output directory.
	"""

	num_retries = 5
	session = requests.Session()
	retry = Retry(total=num_retries, connect=num_retries, read=num_retries, backoff_factor=0.5)
	adapter = HTTPAdapter(max_retries=retry,pool_connections=100, pool_maxsize=200)
	session.mount('http://', adapter)
	session.mount('https://', adapter)
	
	request_headers_https = {
		"Connection": "keep-alive",
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
		"Accept": "*/*",
		"Accept-Encoding": "gzip, deflate, br"
	}
	# "Accept-Language": "en-US,en;q=0.9"

	request_headers_http = {
		"Connection": "keep-alive",
		"User-Agent": "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36",
		"Accept": "*/*"
	}

	raw_lists = {
		'easylist': 'https://easylist.to/easylist/easylist.txt',
		'easyprivacy': 'https://easylist.to/easylist/easyprivacy.txt',
		'antiadblock': 'https://raw.github.com/reek/anti-adblock-killer/master/anti-adblock-killer-filters.txt',
		'blockzilla': 'https://raw.githubusercontent.com/annon79/Blockzilla/master/Blockzilla.txt',
		'fanboyannoyance': 'https://easylist.to/easylist/fanboy-annoyance.txt',
		'fanboysocial': 'https://easylist.to/easylist/fanboy-social.txt',
		'peterlowe': 'http://pgl.yoyo.org/adservers/serverlist.php?hostformat=adblockplus&mimetype=plaintext',
		'squid': 'http://www.squidblacklist.org/downloads/sbl-adblock.acl',
		'warning': 'https://easylist-downloads.adblockplus.org/antiadblockfilters.txt',
	}
	for listname, url in raw_lists.items():
		with open(os.path.join(FILTERLIST_DIR, "%s.txt" % listname), 'wb') as f:
			# f.write(requests.get(url).content)
			try:
				response = session.get(url, timeout=45, headers=request_headers_https)
				response_content = response.content
				f.write(response_content)
			except requests.exceptions.ConnectionError as e1:
				continue



def read_file_newline_stripped(fname):
	try:
		with open(fname) as f:
			lines = f.readlines()
			lines = [x.strip() for x in lines]
		return lines
	except:
		return []



def setup_filterlists():
	'''
	Setup and download (if not already downloaded earlier) the filter lists to identify ad-related URLs
	'''
	FILTERLIST_DIR = "filterlists"
	
	if not os.path.isdir(FILTERLIST_DIR):
		os.makedirs(FILTERLIST_DIR)
	download_lists(FILTERLIST_DIR)
	filterlist_rules = {}
	filterlists = os.listdir(FILTERLIST_DIR)
	
	for fname in filterlists:
		rule_dict = {}
		rules = read_file_newline_stripped(os.path.join(FILTERLIST_DIR, fname))
		rule_dict['script'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['script', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['script_third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'script', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['image'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['image', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['image_third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'image', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['css'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['stylesheet', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['css_third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'stylesheet', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['xmlhttp'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['xmlhttprequest', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['xmlhttp_third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'xmlhttprequest', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['third'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['third-party', 'domain', 'subdocument'], skip_unsupported_rules=False)
		rule_dict['domain'] = AdblockRules(rules, use_re2=False, max_mem=1024*1024*1024, supported_options=['domain', 'subdocument'], skip_unsupported_rules=False)
		filterlist_rules[fname] = rule_dict
	return filterlists, filterlist_rules



def match_url(domain_top_level, current_domain, current_url, resource_type, rules_dict):
	'''
	Associate the URL to a particular category based on different rules
	'''
	try:
		if domain_top_level == current_domain:
			third_party_check = False
		else:
			third_party_check = True
		if resource_type == 'sub_frame':
			subdocument_check = True
		else:
			subdocument_check = False
		if resource_type == 'script':
			if third_party_check:
				rules = rules_dict['script_third']
				options = {'third-party': True, 'script': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			else:
				rules = rules_dict['script']
				options = {'script': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
		elif resource_type == 'image' or resource_type == 'imageset':
			if third_party_check:
				rules = rules_dict['image_third']
				options = {'third-party': True, 'image': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			else:
				rules = rules_dict['image']
				options = {'image': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
		elif resource_type == 'stylesheet':
			if third_party_check:
				rules = rules_dict['css_third']
				options = {'third-party': True, 'stylesheet': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			else:
				rules = rules_dict['css']
				options = {'stylesheet': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
		elif resource_type == 'xmlhttprequest':
			if third_party_check:
				rules = rules_dict['xmlhttp_third']
				options = {'third-party': True, 'xmlhttprequest': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
			else:
				rules = rules_dict['xmlhttp']
				options = {'xmlhttprequest': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
		elif third_party_check:
			rules = rules_dict['third']
			options = {'third-party': True, 'domain': domain_top_level, 'subdocument': subdocument_check}
		else:
			rules = rules_dict['domain']
			options = {'domain': domain_top_level, 'subdocument': subdocument_check}
		return rules.should_block(current_url, options)
	except Exception as e:
		return False



def label_data(script_url):
	'''
	# top_domain = the website being visited
	# script_domain = domain of iframe url
	# script_url = url of iframe
	# resource_type = subframe, image, script
	'''
	top_domain = global_curr_domain
	data_label = False
	filterlists, filterlist_rules = setup_filterlists()
	for fl in filterlists:
		for resource_type in ["sub_frame", "script", "image"]:
			list_label = match_url(top_domain, get_fld(script_url), script_url, resource_type, filterlist_rules[fl])
			data_label = data_label | list_label
			if data_label == True:
				break
		if data_label == True:
			break
	return data_label



def fullpage_screenshot(driver, file, fe):
	'''
	Capture a continuously stitched screenshot of the full webpage being currently visited
	'''

	js = "window.document.styleSheets[0].insertRule(" + "'::-webkit-scrollbar {display: none;}', " + \
			"window.document.styleSheets[0].cssRules.length);"
	try:
		driver.execute_script(js)
		vp_total_height = driver.execute_script("return document.body.parentNode.scrollHeight")
		vp_height = driver.execute_script("return window.innerHeight")
		vp_width = driver.execute_script("return window.innerWidth")
		scale = driver.execute_script("return window.devicePixelRatio")
	except (JavascriptException, WebDriverException) as e:
		error_str = "\nAn Exception Occurred: " + str(e) + " while capturing fullpage sreenshot."
		fe.write(error_str)
		S = lambda X: driver.execute_script('return document.body.parentNode.scroll'+X)
		driver.set_window_size(S('Width'),S('Height')) # May need manual adjustment                                                                                                                
		driver.find_element(By.TAG_NAME, 'body').screenshot(file)
		return False
	
	rectangles_vp = []

	vp = 0
	count, maximum_scrolls = 0, 0
	while vp < vp_total_height:
		count += 1
		if count == maximum_scrolls:
			break
		vp_top_height = vp + vp_height

		if vp_top_height > vp_total_height:
			vp = vp_total_height - vp_height
			vp_top_height = vp_total_height

		rectangles_vp.append((0, vp, 0, vp_top_height))
		vp = vp + vp_height

	stitched_image = Image.new('RGB', (int(vp_width * scale), int(vp_total_height * scale)))

	count = 0
	for i, rect_vp in enumerate(rectangles_vp):
		count += 1
		if count == maximum_scrolls:
			break
		try:
			driver.execute_script("window.scrollTo({0}, {1})".format(0, rect_vp[1]))
			sleep(10)

			tmpfile = "part_{0}.png".format(i)
			driver.get_screenshot_as_file(tmpfile)
			screenshot = Image.open(tmpfile)

			if (i + 1) * vp_height > vp_total_height:
				offset = (0, int((vp_total_height - vp_height) * scale))
			else:
				offset = (0, int(i * vp_height * scale - math.floor(i / 2.0)))

			stitched_image.paste(screenshot, offset)

			del screenshot
			os.remove(tmpfile)
		except:
			continue

	stitched_image.save(file)
	del stitched_image
	return True



def ad_brand_collection(webdriver, domain, ss_image_file_name, brand_exchange_file_name, ad_url_mapping_file_name, fe):
	"""
	Following steps are performed in this function:
	1. Performs three optional commands for bot-detection mitigation when visiting a site 
	2. Saves screenshot of the webpage 
	3. Collects href/iframe URLs from webpage and classfies them ad / non-ad 
	4. Extracts names of brands involved in showing ads to the visited webpage
	"""

	global global_curr_domain;

	# Bot mitigation 1: Move the randomly around a number of times
	try:
		window_size = webdriver.get_window_size()
	except BaseException as error:
		error_str = "\nFunc AD [1]: " + str(error) + " while Bot Mitigation 1 for domain: " + str(domain)
		fe.write(error_str)
		pass
	
	NUM_MOUSE_MOVES = 10
	RANDOM_SLEEP_LOW = 1
	RANDOM_SLEEP_HIGH = 7
	num_moves = 0
	num_fails = 0
	
	while num_moves < NUM_MOUSE_MOVES + 1 and num_fails < NUM_MOUSE_MOVES:
		try:
			if num_moves == 0:  # move to the center of the screen
				x = int(round(window_size["height"] / 2))
				y = int(round(window_size["width"] / 2))
			else:  # move a random amount in some direction
				move_max = random.randint(0, 500)
				x = random.randint(-move_max, move_max)
				y = random.randint(-move_max, move_max)
			action = ActionChains(webdriver)
			action.move_by_offset(x, y)
			action.perform()
			num_moves += 1
		except:
			# MoveTargetOutOfBoundsException
			num_fails += 1
			pass

	# Bot mitigation 2: Scroll in random intervals down page
	try:
		scroll_down(webdriver)
	except BaseException as error:
		error_str = "\nFunc AD [1]: " + str(error) + " while Bot Mitigation 2 for domain: " + str(domain)
		fe.write(error_str)
		pass
	
	try:
		webdriver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
	except (WebDriverException, NoSuchElementException, InvalidSessionIdException) as e:
		error_str = "\nFunc AD [1]: " + str(e) + " while Moving to Top after Bot Mitigation 2 for domain: " + str(domain)
		fe.write(error_str)
		pass

	# Bot mitigation 3: Randomly wait so page visits happen with irregularity
	sleep(random.randrange(RANDOM_SLEEP_LOW, RANDOM_SLEEP_HIGH))

	# Saving Screenshot
	resp = False
	resp = fullpage_screenshot(webdriver, ss_image_file_name, fe)

	try:
		webdriver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
	except (WebDriverException, NoSuchElementException, InvalidSessionIdException) as e:
		error_str = "\nFunc AD [1]: " + str(e) + " while Moving to Top after Bot Mitigation 3 for domain: " + str(domain)
		fe.write(error_str)
		pass
	global_curr_domain = get_fld(domain)
	
	x_offset = y_offset = 15
	missed_urls = []
	exch_brand_url = []
	temp1 = temp2 = temp3 = []

	try:
		temp1 = webdriver.find_elements(By.TAG_NAME, 'a')
		webdriver.execute_script("window.scrollTo(0, (document.body.scrollHeight)/4);")
		sleep(3)
		temp2 = webdriver.find_elements(By.TAG_NAME, 'a')
		webdriver.execute_script("window.scrollTo(0, (3*(document.body.scrollHeight))/4);")
		sleep(3)
		temp3 = webdriver.find_elements(By.TAG_NAME, 'a')
	except BaseException as error:
		error_str = "\nFunc AD [2]: " + str(error) + " while extracting Anchor Tags for domain: " + str(domain)
		fe.write(error_str)
		pass

	if type(temp1) is not list:
		temp1 = []
	if type(temp2) is not list:
		temp2 = []
	if type(temp3) is not list:
		temp3 = []
	anchor_tags = list(set(temp1).union(set(temp2).union(set(temp3))))

	try:
		webdriver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
	except (WebDriverException, NoSuchElementException, InvalidSessionIdException) as e:
		error_str = "\nFunc AD [2]: " + str(e) + " while Moving to Top after Anchor Tag extraction for domain: " + str(domain)
		fe.write(error_str)
		pass

	### print("No of anchor tags present in the web page are: ", len(anchor_tags))
	### print("Extracting href links from anchor tags ...")
	error_str = "\nFunc AD [2]: " + str(len(anchor_tags)) + " Anchor Tags extracted for domain: " + str(domain)
	fe.write(error_str)

	for frame in anchor_tags:
		
		### print(anchor_tags.index(frame))
		action = ActionChains(webdriver)

		try:
			frame_size_dict = frame.rect

			if frame_size_dict["height"] > 10 and frame_size_dict["width"] > 10:
				url = frame.get_attribute("href")

				try:
					curr_fld = str(get_fld(url)).strip()
					if (global_curr_domain == curr_fld) or (curr_fld in ["facebook.com", "instagram.com", "twitter.com", "youtube.com", "linkedin.com", "pinterest.com"]):
						continue
					if not(label_data(url)):
						continue
				except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound) as e:
					fe.write("\nIn a1: " + str(url) + " " + str(e))
					continue
				
				curr_exchange = curr_fld
				missed_urls.append(url)
				### print("Clicking URL in new tab")
				try:
					### print("Trying 1st time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).key_down("t").click().key_up(Keys.CONTROL).key_up("t").perform()
				except:
					fe.write("\nIn a2_1 " + str(url))
					pass
				try:
					### print("Trying 2nd time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).key_down(Keys.TAB).click().key_up(Keys.CONTROL).key_up(Keys.TAB).perform()
				except:
					fe.write("\nIn a2_2 " + str(url))
					pass
				try:
					### print("Trying 3rd time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).send_keys("t").click().key_up(Keys.CONTROL).perform()
				except:
					fe.write("\nIn a2_3 " + str(url))
					pass

				try:
					while (len(webdriver.window_handles)>2):
						webdriver.switch_to.window(webdriver.window_handles[len(webdriver.window_handles)-1])
						webdriver.close()
						webdriver.switch_to.window(webdriver.window_handles[0])
					webdriver.switch_to.window(webdriver.window_handles[1])
					brand = get_fld(webdriver.current_url)
					sleep(2)
					webdriver.close()
				except (IndexError, TimeoutException) as e:
					fe.write("\nIn a3: " + str(url) + str(e))
					continue

				webdriver.switch_to.window(webdriver.window_handles[0])

				temp_string = str(curr_exchange) + ", " + str(brand) + ", " + str(url)
				if (temp_string not in exch_brand_url) and (str(curr_exchange).strip() != str(brand).strip()):
					exch_brand_url.append(temp_string)
					print(curr_exchange, brand) 

			else:
				continue
		except:
			# (StaleElementReferenceException, WebDriverException) as e
			fe.write("\nIn a4")
			continue
	
	### print("Extracted Ads from anchor tags!")

	### print("Now Extracting iframe urls ...")

	try:
		webdriver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
	except (WebDriverException, NoSuchElementException, InvalidSessionIdException) as e:
		error_str = "\nFunc AD [2]: " + str(e) + " while Moving to Top after Anchor Tag Iteration for domain: " + str(domain)
		fe.write(error_str)
		pass

	temp1 = temp2 = temp3 = []
	
	try:
		temp1 = webdriver.find_elements(By.TAG_NAME, 'iframe')
		webdriver.execute_script("window.scrollTo(0, (document.body.scrollHeight)/4);")
		sleep(3)
		temp2 = webdriver.find_elements(By.TAG_NAME, 'iframe')
		webdriver.execute_script("window.scrollTo(0, (3*(document.body.scrollHeight))/4);")
		sleep(3)
		temp3 = webdriver.find_elements(By.TAG_NAME, 'iframe')
	except BaseException as error:
		error_str = "\nFunc AD [3]: " + str(error) + " while extracting iframes for domain: " + str(domain)
		fe.write(error_str)
		pass

	if type(temp1) is not list:
		temp1 = []
	if type(temp2) is not list:
		temp2 = []
	if type(temp3) is not list:
		temp3 = []
	iframes = list(set(temp1).union(set(temp2).union(set(temp3))))

	try:
		webdriver.find_element(By.TAG_NAME, 'body').send_keys(Keys.CONTROL + Keys.HOME)
	except (WebDriverException, NoSuchElementException, InvalidSessionIdException) as e:
		error_str = "\nFunc AD [3]: " + str(e) + " while Moving to Top after iframe extraction for domain: " + str(domain)
		fe.write(error_str)
		pass

	### print("No of frames present in the web page are: ", len(iframes))
	error_str = "\nFunc AD [3]: " + str(len(iframes)) + " iframes extracted for domain: " + str(domain)
	fe.write(error_str)

	for frame in iframes:
		
		### print(iframes.index(frame))
		action = ActionChains(webdriver)

		try:
			frame_size_dict = frame.rect

			if frame_size_dict["height"] > 10 and frame_size_dict["width"] > 10: 	
				url = frame.get_attribute("src")
				missed_urls.append(url)

				try:
					curr_fld = get_fld(url)
					if global_curr_domain == curr_fld:
						continue
					if not(label_data(url)):
						continue
				except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound) as e:
					fe.write("\nIn i1: " + str(url) + str(e))
					continue
				
				try:
					curr_exchange = str(curr_fld).strip()
				except tld.exceptions.TldBadUrl as e:
					fe.write("\nIn i2: " + str(url) + str(e))
					continue

				### print("Clicking URL in new tab")
				try:
					### print("Trying 1st time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).key_down("t").click().key_up(Keys.CONTROL).key_up("t").perform()
				except:
					fe.write("\nIn i3_1 " + str(url))
					pass
				try:
					### print("Trying 2nd time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).key_down(Keys.TAB).click().key_up(Keys.CONTROL).key_up(Keys.TAB).perform()
				except:
					fe.write("\nIn i3_2 " + str(url))
					pass
				try:
					### print("Trying 3rd time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).send_keys("t").click().key_up(Keys.CONTROL).perform()
				except:
					fe.write("\nIn i3_3 " + str(url))
					pass

				try:
					while (len(webdriver.window_handles)>2):
						webdriver.switch_to.window(webdriver.window_handles[len(webdriver.window_handles)-1])
						webdriver.close()
						webdriver.switch_to.window(webdriver.window_handles[0])
					webdriver.switch_to.window(webdriver.window_handles[1])
					brand = get_fld(webdriver.current_url)
					sleep(2)
					webdriver.close()
				except (IndexError, TimeoutException) as e:
					fe.write("\nIn i4: " + str(url) + str(e))
					continue

				webdriver.switch_to.window(webdriver.window_handles[0])

				temp_string = str(curr_exchange) + ", " + str(brand) + ", " + str(url)
				if (temp_string not in exch_brand_url) and (str(curr_exchange).strip() != str(brand).strip()):
					exch_brand_url.append(temp_string)
					print(curr_exchange, brand) 

			else:
				continue
		except:
			# (StaleElementReferenceException, WebDriverException) as e
			fe.write("\nIn i5")
			continue
	try:
		webdriver.quit()
	except Exception as e:
		pass

	### print("Extracted Ads from iframes!")
	
	### print("Now visitng missed urls ...")

	error_str = "\nFunc AD [4]: " + str(len(missed_urls)) + " missed_urls being traversed for domain: " + str(domain)
	fe.write(error_str)

	for url in missed_urls:

		try:
			orig_fld = curr_exchange = str(get_fld(url)).strip()
		except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound) as e:
			fe.write("\nIn m1: " + str(url) + str(e))
			continue

		try:
			webdriver = Chrome(executable_path="./chromedriver", options=chrome_options)
			webdriver.get(url)
		except (TimeoutException, WebDriverException) as e:
			fe.write("\nIn m2: " + str(url) + str(e))
			try:
				webdriver.quit()
			except Exception as e:
				pass
			continue
		sleep(3)

		try:
			redirected_fld = str(get_fld(webdriver.current_url)).strip()
		except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound, TimeoutException) as e:
			try:
				webdriver.quit()
			except Exception as e:
				pass
			fe.write("\nIn m3: " + str(url) + str(e))
			continue

		# Ignoring some common false positive cases
		if url in ["https://help.revcontent.com/en/knowledge/revcontent-privacy-policy","https://googleads.g.doubleclick.net/pagead/html/r20211111/r20190131/zrt_lookup.html","https://www.revcontent.com/popup?utm_source=ads&utm_medium=organic&utm_term=signup","https://help.revcontent.com/en/knowledge/fake-news-complaints"] or "www.amazon.com" in url or "feedburner.com" in url:
			try:
				webdriver.quit()
			except Exception as e:
				pass
			continue

		temp_url_list = []
		# Process lockerdome & bannersnack URL differently as it doesnt directly lead to the advertiser's page
		if "bannersnack" in url:
			try:
				element_to_click = webdriver.find_element(By.XPATH, '//div[@class="slide-inner"]')
			except:
				fe.write("\nIn m4_b1 bannersnack: " + str(url))
				pass
			# action = ActionChains(webdriver)
			try:
				# action.move_to_element(element_to_click).move_by_offset(x_offset, y_offset).click().perform()
				element_to_click.click()
				sleep(2)
			except:
				fe.write("\nIn m4_b2 bannersnack: " + str(url))
				pass
			try:
				webdriver.switch_to.window(webdriver.window_handles[1])
				curr_url = webdriver.current_url
				brand = get_fld(curr_url)
			except (IndexError, TimeoutException) as e:
				fe.write("\nIn m4_b3 bannersnack: " + str(url) + str(e))
				continue

			temp_string = str(curr_exchange) + ", " + str(brand) + ", " + str(curr_url)
			if (temp_string not in exch_brand_url) and (str(curr_exchange).strip() != str(brand).strip()):
				exch_brand_url.append(temp_string)
				print(curr_exchange, brand) 
		
		elif "lockerdome" in url:
			subads = []
			try:
				subads = webdriver.find_elements(By.XPATH, '//div[@data-li]')
			except:
				fe.write("\nIn m5_l1 lockerdome: " + str(url))
				pass
			action = ActionChains(webdriver)
			
			for frame in subads:
				### print("Clicking URL in a new tab")
				try:
					### print("Trying 1st time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).key_down("t").click().key_up(Keys.CONTROL).key_up("t").perform()
				except:
					fe.write("\nIn m5_l2 lockerdome: " + str(url))
					pass
				try:
					### print("Trying 2nd time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).key_down(Keys.TAB).click().key_up(Keys.CONTROL).key_up(Keys.TAB).perform()
				except:
					fe.write("\nIn m5_l3 lockerdome: " + str(url))
					pass
				try:
					### print("Trying 3rd time")
					action.move_to_element(frame).move_by_offset(x_offset, y_offset).key_down(Keys.CONTROL).send_keys("t").click().key_up(Keys.CONTROL).perform()
				except:
					fe.write("\nIn m5_l4 lockerdome: " + str(url))
					pass

				try:
					while (len(webdriver.window_handles)>2):
						webdriver.switch_to.window(webdriver.window_handles[len(webdriver.window_handles)-1])
						webdriver.close()
						webdriver.switch_to.window(webdriver.window_handles[0])
					webdriver.switch_to.window(webdriver.window_handles[1])
					curr_url = webdriver.current_url
					brand = get_fld(curr_url)
					sleep(2)
					webdriver.close()
				except (IndexError, TimeoutException) as e:
					fe.write("\nIn m5_l5 lockerdome: " + str(url) + " " + str(e))
					continue

				webdriver.switch_to.window(webdriver.window_handles[0])

				temp_string = str(curr_exchange) + ", " + str(brand) + ", " + str(curr_url)
				if (temp_string not in exch_brand_url) and (str(curr_exchange).strip() != str(brand).strip()):
					exch_brand_url.append(temp_string)
					print(curr_exchange, brand) ### 

		else:
			if (orig_fld == redirected_fld):
				try:
					links = webdriver.find_elements(By.TAG_NAME, "a")
				except:
					fe.write("\nIn m6: " + str(url))
					links = []
					pass

				if len(links) > 50:
					try:
						webdriver.quit()
					except Exception as e:
						pass
					continue

				for link in links:
					url_new = link.get_attribute("href")
					try:
						if get_fld(url_new) in ["facebook.com", "instagram.com", "twitter.com", "youtube.com", "linkedin.com", "pinterest.com"] or "adssettings.google.com" in url_new:
							continue
						else:
							temp_url_list.append(url_new)
					except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound) as e:
						fe.write("\nIn m7: " + str(url) + str(e))
						continue
		try:
			webdriver.quit()
		except Exception as e:
			pass


		brand_temp = []
		seen_urls = []
		for u in temp_url_list:
			try:
				webdriver = Chrome(executable_path="./chromedriver", options=chrome_options)
			except:
				fe.write("\nIn m8: " + str(u))
				continue

			try:
				if u not in seen_urls:
					webdriver.get(u)
					seen_urls.append(u)
				else:
					webdriver.quit()
					continue
			except (TimeoutException, WebDriverException) as e:
				fe.write("In m9: " + str(u) + " " + str(e))
				try:
					webdriver.quit()
				except Exception as e:
					pass
				continue
			sleep(3)

			try:
				brand_temp.append(str(get_fld(webdriver.current_url)).strip())
			except (tld.exceptions.TldBadUrl, tld.exceptions.TldDomainNotFound) as e:
				fe.write("\nIn m10: " + str(u) + " " + str(e))
				try:
					webdriver.quit()
				except Exception as e:
					pass
				continue

			try:
				webdriver.quit()
			except Exception as e:
				pass

		
		seen_urls = []
		temp_url_list = []

		if len(brand_temp) != 0:
			for brandd in brand_temp:
				temp_string = str(curr_exchange) + ", " + str(brandd) + ", " + str(url)
				if (temp_string not in exch_brand_url) and (str(curr_exchange).strip() != str(brandd).strip()):
					exch_brand_url.append(temp_string)
					print(curr_exchange, brandd) 
		else:
			temp_string = str(curr_exchange) + ", " + str(redirected_fld) + ", " + str(url)
			if (temp_string not in exch_brand_url) and (str(curr_exchange).strip() != str(redirected_fld).strip()):
				exch_brand_url.append(temp_string)
				print(curr_exchange, redirected_fld) 

	missed_urls = []
	
	### print("Missed urls extracted!")

	if len(exch_brand_url) != 0:
	
		f = open(ad_url_mapping_file_name, "w")
		fm = open(brand_exchange_file_name, "w")

		tmp = []
		for i in range(len(exch_brand_url) - 1):
			l = exch_brand_url[i].split(", ")
			exchange = str(l[0])
			brand = str(l[1])
			comb = exchange + ", " + brand 
			if comb not in tmp:
				fm.write(comb)
				fm.write("\n")
				tmp.append(comb)
			f.write(exch_brand_url[i])
			f.write("\n")
		f.write(exch_brand_url[len(exch_brand_url) - 1])
		comb = ", ".join(exch_brand_url[len(exch_brand_url) - 1].split(", ")[:2])
		if comb not in tmp:
			fm.write(comb)

		f.close()
		fm.close()

	exch_brand_url = []
	
	### print("Ad details saved to a file!")



def save_bidding_json(filename, data):
	'''
	Save Bidding related data
	'''
	with open(filename, 'w') as f:
		json.dump(data, f, indent=4)
	f.close()



def get_header_bidding_bid_information(driver, site, filename, fe):
	'''
	Collect Header Bidding Information based on the prebid.js
	'''
	row = {
		'HB_URL': site
	}

	# Find pbjs var
	try:
		pbjsGlobal = driver.execute_script('return _pbjsGlobals')[0]
		# Find methods for pbjs
		methods = driver.execute_script('return Object.keys(%s).filter(x => typeof(%s[x]) == "function")' % (pbjsGlobal, pbjsGlobal))
		# Store each methods response
		for method in methods:
			try:
				row[method] = json.dumps(driver.execute_script('return %s.%s()' % (pbjsGlobal, method)))
			except:
				pass

		save_bidding_json(filename, row)
		### print("HB Information Collected!")
	except (JavascriptException, WebDriverException) as e:
		### print("No HB Detected on this site!")
		error_str = "\nAn exception occurred: " + str(e) + " while collecting HB Info for domain: " + str(site)
		fe.write(error_str)



def crawler_function(driver, site, ss_image_file, brand_exchange_file, ad_url_mapping_file, har_file, hb_file, proxy, fe):

	try:
		driver.get(site)
	except (TimeoutException, WebDriverException) as e:
		error_str = "\nAn exception occurred: " + str(e) + " while getting the domain: " + str(site)
		fe.write(error_str)
		driver.close()
		driver.quit()
		return

	### print("Sleeping for 30s for website to load completely!")
	sleep(30)
	### print("Obtaining Header Bidding related information from the prebid.js")
	get_header_bidding_bid_information(driver, site, hb_file, fe)

	# Save HAR Files
	try:
		with open(har_file + '.har', 'w') as har_f:
			json.dump(proxy.har, har_f, indent=4)
		### print("HAR Dump extracted!")
	except BaseException as error:
		### print("HAR Dump not extracted!")
		error_str = "\nAn exception occurred: " + str(error) + " while dumping the HAR for domain: " + str(site)
		fe.write(error_str)
		pass

	# Collect ad brands from the webpage
	try:
		ad_brand_collection(driver, site, ss_image_file, brand_exchange_file, ad_url_mapping_file, fe)
		### print("Ad Brands extracted!")
	except BaseException as error:
		error_str = "\nAn exception occurred: " + str(error) + " in Ad Brand Collection for domain: " + str(site)
		fe.write(error_str)



def main(agent_index, crawl_number, directory, urls):
	'''
	Main function to crawl the webpage, brands running ads on it, and screenshot it 
	'''

	todays_date = datetime.date.today()
	date = "|" + str(todays_date.day) + "_" + str(todays_date.month) + "_" + str(todays_date.year)
	print(len(urls))

	for domain in urls:

		print(urls.index(domain), domain, "started")

		domain_name = domain.strip().replace("https://","").replace("http://","").replace("www.","").strip(".").replace(".","_").replace("/","_")
		
		file_directory = directory + "/" + domain_name
		if not os.path.exists(file_directory):
			os.makedirs(file_directory)

		error_file = file_directory + "/" + crawl_number + "|error|" + domain_name + ".txt"
		fe = open(error_file, "w")

		# Instatiate and start browsermobproxy to collect HAR files
		try:
			server = Server("browsermob-proxy-2.1.4/bin/browsermob-proxy", options={'port': 8022})
			server.start()
			proxy = server.create_proxy()
		except BaseException as error:
			error_str = "\nAn exception occurred: " + str(error) + " while initiating and starting the BrowserMob Proxy Server for domain: " + str(domain)
			fe.write(error_str)
			fe.close()
			print(domain, "ended")
			continue
		
		# Commands to kill running background process: lsof -i tcp:8020 OR kill -9 9920
		# Associate proxy-related settings to the chromedriver
		chrome_options.add_argument("--proxy-server={}".format(proxy.proxy))
		chrome_options.add_argument('--ignore-ssl-errors=yes')
		chrome_options.add_argument('--use-littleproxy false')
		chrome_options.add_argument("--proxy=127.0.0.1:%s" % proxy.port)

		# Start the chromedriver instance
		try:
			driver = webdriver.Chrome(executable_path="./chromedriver", options=chrome_options)
		except BaseException as error:
			server.stop()
			error_str = "\nAn exception occurred: " + str(error) + " while initializing the webdriver for domain: " + str(domain)
			fe.write(error_str)
			fe.close()
			print(domain, "ended")
			continue
		### print("\nDrive has been successfully loaded!\n")

		# Creating filenames of different output files associated with the current website
		ss_image_f = file_directory + "/" + crawl_number + "|ss|" + domain_name + date + ".png"
		brand_exchange_f = file_directory + "/" + crawl_number + "|brand|" + domain_name + date + ".txt"
		ad_url_mapping_f = file_directory + "/" + crawl_number + "|mapping|" + domain_name + date + ".txt"
		har_file = file_directory + "/" + crawl_number + "|har|" + domain_name + date
		hb_file = file_directory + "/" + crawl_number + "|hb|" + domain_name + date + ".json"
		try:
			proxy.new_har(har_file, options={'captureHeaders': True,'captureContent':True})
		except BaseException as error:
			error_str = "\nAn exception occurred: " + str(error) + " while creating a new HAR File for domain: " + str(domain)
			fe.write(error_str)
			pass
		
		# Capture the screenshot of the page, brand names, and HAR files
		try:
			crawler_function(driver, domain, ss_image_f, brand_exchange_f, ad_url_mapping_f, har_file, hb_file, proxy, fe)
		except BaseException as error:
			### print('An exception occurred: {} for domain: {}.'.format(error, domain))
			error_str = "\nAn exception occurred: " + str(error) + " in Crawler Function for domain: " + str(domain)
			fe.write(error_str)
			fe.close()
			server.stop()
			print(domain, "ended")
			continue

		try:
			driver.close()
		except Exception as e:
			pass
		sleep(1)
		try:
			driver.quit()
		except Exception as e:
			pass
		
		fe.close()
		server.stop()
		print(domain, "ended")



def parse_args():
	'''
	Parse arguments passed for different threads by multi-processing code
	'''
	parser = ArgumentParser()
	parser.add_argument('crawlNumber')
	parser.add_argument('urls')
	parser.add_argument('agentId')
	parser.add_argument('crawlDirectory')
	return parser.parse_args()



if __name__ == '__main__':
	
	args = parse_args()
	urls = args.urls.split(',')

	df = main(args.agentId, args.crawlNumber, args.crawlDirectory, urls)
