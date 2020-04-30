import json
import queue
import re
import datetime
import PyPDF2
import shutil


def change_first_line(file_name):
    with open(file_name, "r") as f:
        from_file = f.read()
        # replace this string once
        from_file = from_file.replace("window.YTD.ad_impressions.part0 =", "", 1)
    with open(file_name, "w") as f:
        f.write(from_file)
    
    
def categorizations(ads):
    '''
    Takes an ad-impressions.json and returns a dictionary of dictionaries in 
    the structure {"targeting_type": {"targeting_value": number_of_appearances}}
    Optionally, returns only the matched criteria appearing over a certain 
    number of times.

    Inputs:
        ads: a readable json, the result of calling json.loads(f.read())

    Outputs: 
        A dictionary of dictionaries of integers, as described above.
    '''
    all_matches = dict()

    for ad in ads:
        ad_list = ad["ad"]["adsUserData"]["adImpressions"]["impressions"]
        for impression in ad_list:
            if "matchedTargetingCriteria" not in impression.keys():
                continue
            criteria = impression["matchedTargetingCriteria"]

            for target in criteria:
                ttype = target["targetingType"]
                if "targetingValue" not in target.keys():
                    continue
                tvalue = target["targetingValue"]
                if ttype not in all_matches.keys():
                    all_matches[ttype] = dict()
                all_matches[ttype][tvalue] = all_matches[ttype].get(tvalue, 0) + 1

    return all_matches


def min_matches(matched_dict, min_val):
    '''
    Takes an ad-impressions dictionary (output of categorizations) and returns
    only keys where targeting values are above the minimum threshold min_val.

    Inputs:
        matched_dict: a dictionary of dictionaries of integers, the output of
            the categorizations function.
        min_val: an integer, the minimum number of times targeting values must
            appear in the matched_dict to be included.

    Outputs:
        submatches: a dictionary in the same structure as the input 
            matched_dict, but with only keys containing targeting values above 
            the user inputted minimum threshold.
    '''

    submatches = dict()

    for match_type, val in matched_dict.items():
        minmatches = dict()

        for match, n in val.items():
            if n > min_val:
                minmatches[match] = n

        if len(minmatches) > 0:
            submatches[match_type] = minmatches

    return submatches


def top_k_matches(matched_dict, k):
    '''
    For each targeting criteria, returns only the top k values. Ties are broken
    by first appearance.

    Inputs:
        matched_dict: a dictionary of dictionaries of integers, the output of
            the categorizations function.
        k: an integer, the desired number of top matches to show.

    Outputs:
        top_matches: a dictionary in the same structure as the input 
            matched_dict, but with only the top k keys.
    '''

    top_matches = dict()

    for match_type, val in matched_dict.items():
        top_k = queue.PriorityQueue(maxsize = k)
        subgroup_topk = dict()

        for match, n in val.items():
            if not top_k.full():
                top_k.put((n, match))
            else:
                low, name_low = top_k.get()
                if n > low:
                    top_k.put((n, match))
                else:
                    top_k.put((low, name_low))

        while not top_k.empty():
            top_val, top_name = top_k.get()
            subgroup_topk[top_name] = top_val

        top_matches[match_type] = subgroup_topk

    return top_matches


def num_umatched(ads):
    '''
    Finds the number of ads without matched targeting criteria.

    Inputs:
        ads: a readable json, the result of calling json.loads(f.read())

    Outputs:
        a tuple. The first element of the tuple is the total number of ads in 
            the ad impressions file. The second element is the number of 
            unmatched ads in the ad impressions file.
    '''

    total_unmatched = 0
    total_ads = 0

    for ad in ads:
        ad_list = ad["ad"]["adsUserData"]["adImpressions"]["impressions"]
        for impression in ad_list:
            total_ads += 1
            if "matchedTargetingCriteria" not in impression.keys():
                total_unmatched += 1

    return (total_ads, total_unmatched)


def count_companies(ads):
    '''
    Counts the number of times a company advertised to a user.

    Inputs:
        ads: a readable json, the result of calling json.loads(f.read())

    Outputs:
        A dictionary, where keys are company handles and values are the number
            of times that company advertised to a specific user.
    '''

    companies = dict()

    for ad in ads:
        ad_list = ad["ad"]["adsUserData"]["adImpressions"]["impressions"]
        for impression in ad_list:
            if "screenName" in impression["advertiserInfo"].keys():
                screen_name = impression["advertiserInfo"]["screenName"]
                companies[screen_name] = companies.get(screen_name, 0) + 1

    return companies 


def top_k_companies(ads, k):
    '''
    Takes a company dictionary and returns the top k advertising companies

    Inputs:
        ads: a readable json, the result of calling json.loads(f.read())
        k: an integer, the desired number of top companies to show.

    Outputs:
        a company_dict, only showing the top k companies.
    '''

    top_k = queue.PriorityQueue(maxsize = k)
    top_companies = dict()
    company_dict = count_companies(ads)

    for comp, count in company_dict.items():
        if not top_k.full():
            top_k.put((count, comp))
        else:
            low_count, low_comp = top_k.get()
            if count > low_count:
                top_k.put((count, comp))
            else:
                top_k.put((low_count, low_comp))

    while not top_k.empty():
        top_count, top_comp = top_k.get()
        top_companies[top_comp] = top_count

    return top_companies


def date_range(ads):
    '''
    Computes the first and last ad seen in the ad-impressions data.

    Inputs:
        ads: a readable json, the result of calling json.loads(f.read())

    Outputs:
        first: a datetime.date object with the earliest seen ad.
        last: a datetime.date object with the latest seen ad.
    '''

    last = datetime.date(2000, 1, 1)
    first = datetime.date(2050, 1, 1)
    DATE = re.compile(r"(\d{4})-(\d{2})-(\d{2})")

    for ad in ads:
        ad_list = ad["ad"]["adsUserData"]["adImpressions"]["impressions"]
        for ad in ad_list:
            im = DATE.findall(ad["impressionTime"])[0]
            im = [int(i) for i in im]
            time = datetime.date(im[0], im[1], im[2])
            if time > last:
                last = time
            elif time < first:
                first = time

    return first, last


def num_targeted(ads):
    '''
    Calculates the approximate total of ads in the ad-impressions file where you
    are on a tailored audience list.

    Inputs:
        ads: a readable json, the result of calling json.loads(f.read())

    Outputs:
        num_targeted: an approximate count of the number of ads that put you on
            a tailored audience list.
    '''

    num_targeted = 0

    for ad in ads:
        ad_list = ad["ad"]["adsUserData"]["adImpressions"]["impressions"]
        for ad in ad_list:
            if "matchedTargetingCriteria" in ad.keys():
                for match in ad["matchedTargetingCriteria"]:
                    if match["targetingType"] == "Tailored audiences (lists)" or \
                        match["targetingType"] == "Tailored audiences (web)":
                        num_targeted += 1
                        break
                        

    return num_targeted


def avg_num_targeted(ads):
    '''
    Finds the average number of targeting criteria used per ad.

    Inputs:
        ads: a readable json, the result of calling json.loads(f.read())

    Outputs:
        a float, the average number of targeting criteria used per ad.
    '''

    total_num_ads = 0
    total_num_targets = 0

    for ad in ads:
        ad_list = ad["ad"]["adsUserData"]["adImpressions"]["impressions"]
        for ad in ad_list:
            total_num_ads += 1
            if "matchedTargetingCriteria" in ad.keys():
                total_num_targets += len(ad["matchedTargetingCriteria"])

    return total_num_targets / total_num_ads


def match_tailored(advertiser_file, matched_dict):
    '''
    Compares twitter's front-end view of who you are a similar audience to
    to the backend "Follower Look-alikes" list you are on.

    Inputs:
        advertiser_file: "twitter_advertiser_list" pdf file name
        matched_dict: a dictionary of dictionaries of integers, the output of
            the categorizations function.

    Outputs:
        the disimilarities between the frontend and backend
    '''

    ats = []
    AT_PAT_0 = re.compile(r"these audiences\.(.+)")
    AT_PAT_1 = re.compile(r"(@\w+)")
    look_alikes = matched_dict["Follower look-alikes"].keys()

    pdf = open(advertiser_file, "rb")
    pdfr = PyPDF2.PdfFileReader(pdf) 

    for page in range(pdfr.numPages - 1):
        pg = pdfr.getPage(page)
        text = pg.extractText()
        if page == 0:
            text = AT_PAT_0.findall(text)[0]
        new_ats = AT_PAT_1.findall(text)
        ats.extend(new_ats)

    only_frontend = [i for i in ats if i not in look_alikes]
    only_backend = [i for i in look_alikes if i not in ats]
    both = [i for i in ats if i in look_alikes]

    return only_frontend, only_backend


def format_output(file_name):
    '''
    Takes an ad-impressions file and prints summary info about the file.

    Inputs:
        file_name: name of the ad-impressions.js file

    Outputs:
        None, just prints summary info.
    '''

    change_first_line(file_name)

    with open(file_name, "r") as f:
        ads = json.loads(f.read())

    matched_dict = categorizations(ads)
    top_matches = top_k_matches(matched_dict, 5)
    top_companies = top_k_companies(ads, 10)
    total, unmatched = num_umatched(ads)
    targeted = num_targeted(ads)
    avg = avg_num_targeted(ads)
    first, last = date_range(ads)
    first = "{} {}, {}".format(first.strftime("%B"), first.day, first.year)
    last = "{} {}, {}".format(last.strftime("%B"), last.day, last.year)

    '''
    a = ("From {} to {}, there were {} targeted ads in your data ({} total)."
        " On average, each ad had {:.2f} targeting criteria."
        " Of those, advertisers wanted to reach you the most in the following "
        "categories: \n \n").format(first, last, total - unmatched, total, avg)

    b = ("Interests: {} \n \nFollower look-alikes: {} \n \nEvents: {} \n \n" 
        "Keywords: {} \n \nBehaviors: {} \n \n").format(
        top_matches["Interests"],\
        top_matches["Follower look-alikes"], top_matches["Events"], \
        top_matches["Keywords"], top_matches["Behaviors"])

    c = "The top 10 companies advertising to you were {}".format(top_companies)

    d = ("\n \nThere were approximately {} ads targeted to you from tailored"
        " audience lists, making up {:.2f}% of all ads you saw").format(targeted, targeted/total*100)
    '''

    f.close()

    return first, last, total - unmatched, total, avg, top_matches["Interests"], \
        top_matches["Follower look-alikes"], top_matches["Events"], top_matches["Keywords"], top_matches["Behaviors"], \
        top_companies, targeted, targeted/total*100


