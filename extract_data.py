# /// script
# requires-python = ">=3.11,<3.12"
# dependencies = [
#     "pytz",
#     "urllib3==1.26.16",
#     "requests==2.32.2",
#     "selenium<4",
# ]
# ///


from selenium import webdriver
from selenium.webdriver import FirefoxOptions
from os.path import join as pjoin, dirname, isdir, exists
from os import makedirs
from dataclasses import dataclass
import time
import json
import pytz
import os
from datetime import date

@dataclass
class FBQuery:
    name: str
    url: str
    id: int
    category: str
    
follower_suffix_len = len(' followers')

def extract_followers(txt: str):
    suffix = ' followers'    
    val = txt[0:-follower_suffix_len]
    try:
        ret = int(val)
    except:
        val = val.lower()
        if val.endswith('k'):
            ret = int(float(val[:-1]) * 1000)
        elif val.endswith('m'):
            ret = int(float(val[:-1]) * 1000000)
        else:
            raise Exception('unexpected fb follower format')
    return ret

def get_stats_filepath(basedir):
    from datetime import datetime
    cdate = date.today().isoformat()
    return pjoin(basedir, f"{cdate}-stats.json")

def main():
    # todo: use env var + default to set driver_loc, data_Loc, and toquery_loc
    driver_loc = pjoin(dirname(__file__), 'geckodriver')
    data_loc = pjoin(dirname(__file__), 'data')
    toquery_loc = pjoin(dirname(__file__), 'toquery_updated_v2.json')
    makedirs(data_loc, exist_ok=True)
    stats_filepath = get_stats_filepath(data_loc)
    if exists(stats_filepath):
        print(f"file already exists: {stats_filepath}")
        return
    # print(f'driver_loc = {driver_loc}')
    with open(toquery_loc) as f:
        fb_url_list = [
            FBQuery(o['name'], o['url'], o['id'], o['category']) for o in json.load(f)
        ]
    options = FirefoxOptions()
    options.add_argument('-headless')
    driver = webdriver.Firefox(options=options)
    
    # print('af fb')
    driver.implicitly_wait(3)
    for seq, o in enumerate(fb_url_list):
        # if o.id != 43:
        #     continue
        print(f'[{seq + 1}/{len(fb_url_list)}] For {o.name}: {o.url}')
        driver.get(o.url)
        elts = driver.find_elements_by_css_selector('a[href$="/followers/"]')
        if elts is None:
            continue
        with open(stats_filepath, "a") as f:
            for elt in elts:
                # print(type(elt.text))
                data = json.dumps({
                    'url': o.url,
                    'name': o.name,
                    'id': o.id,
                    'category': o.category,
                    'date': date.today().isoformat(),
                    'followers': extract_followers(elt.text)
                })
                print(data, file=f)
            
    driver.quit()    


if __name__ == "__main__":
    main()
