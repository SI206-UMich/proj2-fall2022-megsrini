#Name: Meghana Srinivasa 
from xml.sax import parseString
from bs4 import BeautifulSoup
import re
import os
import csv
import unittest


def get_listings_from_search_results(html_file):
    listing_title = []
    first_price_list = []
    final_price_list = []
    first_url_list = []
    id_list = []
    page = open(html_file)
    soup = BeautifulSoup(page,'html.parser')
    title_list = soup.find_all('div',class_="t1jojoys dir dir-ltr")
    for title in title_list: 
        listing_title.append(title.text)  
    price_list = soup.find_all('span',class_="_tyxjp1")
    for price in price_list: 
        first_price_list.append(price.text)
    for price in first_price_list:
        price = int(price[1:])
        final_price_list.append(price)
    url_list = soup.find_all("meta",itemprop="url")
    for url in url_list: 
        first_url_list.append(url.get('content'))
    for url in first_url_list:
        id = re.findall('\d{7,}',url)
        id_list.extend(id)
    final = list(zip(listing_title, final_price_list, id_list))
    page.close()
    return final


def get_listing_information(listing_id):
    number_list = []
    type_list = []
    first_room_list = []
    final_room_list = []
    page = open('html_files/listing_'+listing_id+'.html')
    soup = BeautifulSoup(page,'html.parser')
    policy_number_list = soup.find_all('li',class_="f19phm7j dir dir-ltr")
    for policy in policy_number_list:
        number = policy.find('span',class_="ll4r2nl dir dir-ltr")
        number_list.append(number.text)
    policy_number = number_list[0]
    if "Exempt" in policy_number:
        policy_number = "Exempt"
    elif "not needed" in policy_number:
        policy_number = 'Exempt'
    elif "Pending" in policy_number: 
        policy_number = "Pending"
    elif "pending" in policy_number: 
        policy_number = "Pending"
    else: 
        policy_number = number_list[0]
    place_list = soup.find_all('h2',class_="_14i3z6h")
    for place in place_list: 
        type_list.append(place.text)
    place_type = type_list[0]
    if "Private" in place_type:
        place_type = "Private Room"
    elif "private" in place_type:
        place_type = "Private Room"
    elif "Shared" in place_type: 
        place_type = "Shared Room"
    elif "shared" in place_type: 
        place_type = "Shared Room"
    else: 
        place_type = "Entire Room"
    room_list = soup.find_all('li',class_="l7n4lsf dir dir-ltr")
    for rooms in room_list:
        first_room_list.append(rooms.text)
    for rooms in first_room_list:
        room = re.findall('\d [a-z]* *bedroom',rooms)
        room1 = re.findall('Studio*',rooms)
        final_room_list.extend(room) 
        final_room_list.extend(room1) 
    if 'Studio' in final_room_list[0]:
        bedroom = 1
    else: 
        bedroom = int(final_room_list[0][0])
    page.close()
    final = (policy_number,place_type,bedroom)  
    return final

def get_detailed_listing_database(html_file):
    listing_id_list = []
    first_function = get_listings_from_search_results(html_file)
    second_function = []
    final = []
    for tuple in first_function: 
        listing_id_list.append(tuple[-1])
    for id in listing_id_list:
        second_function.append(get_listing_information(id))
    for i in range(len(first_function)): 
        final.append(first_function[i]+second_function[i])
    return final

def write_csv(data, filename):
    data.sort(key = lambda x: x[1])
    headers = ["Listing Title", "Cost", "Listing ID", "Policy Number", "Place Type", "Number of Bedrooms"]
    f = open(filename, 'w')
    writer = csv.writer(f)
    writer.writerow(headers)
    for tuple in data: 
        writer.writerow(tuple)
    f.close()


def check_policy_numbers(data):
    list_of_policy_numbers = []
    correct_numbers = []
    final  = []
    for i in data: 
        list_of_policy_numbers.append(i[3])
    for number in list_of_policy_numbers:
            correct_numbers.extend(re.findall("20\d\d-00\d\d\d\dSTR", number))
            correct_numbers.extend(re.findall("STR-000\d\d\d\d", number))
            correct_numbers.extend(re.findall("Pending", number))
            correct_numbers.extend(re.findall("Exempt", number))
    for num in list_of_policy_numbers: 
        if num not in correct_numbers: 
            incorrect_number= num
    for num in data: 
        if num[3] == incorrect_number: 
            final.append(num[2])
    print(final)
    return final
    
def extra_credit(listing_id):
    month_date = []
    count = 0
    review_dic = {}
    page = open('html_files/listing_'+listing_id+'_reviews.html')
    soup = BeautifulSoup(page,'html.parser')
    review_list = soup.find_all('li',class_="_1f1oir5")
    for review in review_list:
        month_date.append(review.text)  
    for i in month_date:
        if i[-4:] not in review_dic: 
            review_dic[i[-4:]] = 1
        else: 
            review_dic[i[-4:]] +=1
    final = dict(sorted(review_dic.items(), key=lambda item: item[1], reverse = True))
    page.close()
    if list(final.values())[0]>90: 
        return False
    else: 
        return True

class TestCases(unittest.TestCase):

    def test_get_listings_from_search_results(self):
        # call get_listings_from_search_results("html_files/mission_district_search_results.html")
        # and save to a local variable
        listings = get_listings_from_search_results("html_files/mission_district_search_results.html")
        # check that the number of listings extracted is correct (20 listings)
        self.assertEqual(len(listings), 20)
        # check that the variable you saved after calling the function is a list
        self.assertEqual(type(listings), list)
        # check that each item in the list is a tuple
        self.assertTrue(type(i) is tuple for i in listings)
        # check that the first title, cost, and listing id tuple is correct (open the search results html and find it)
        self.assertEqual(('Loft in Mission District',210,'1944564'),listings[0])
        # check that the last title is correct (open the search results html and find it)
        self.assertEqual(('Guest suite in Mission District',238,'32871760'),listings[-1])

    def test_get_listing_information(self):
        html_list = ["1623609",
                     "1944564",
                     "1550913",
                     "4616596",
                     "6600081"]
        # call get_listing_information for i in html_list:
        listing_informations = [get_listing_information(id) for id in html_list]
        # check that the number of listing information is correct (5)
        self.assertEqual(len(listing_informations), 5)
        for listing_information in listing_informations:
            # check that each item in the list is a tuple
            self.assertEqual(type(listing_information), tuple)
            # check that each tuple has 3 elements
            self.assertEqual(len(listing_information), 3)
            # check that the first two elements in the tuple are string
            self.assertEqual(type(listing_information[0]), str)
            self.assertEqual(type(listing_information[1]), str)
            # check that the third element in the tuple is an int
            self.assertEqual(type(listing_information[2]), int)
        # check that the first listing in the html_list has policy number 'STR-0001541'
        self.assertEqual(listing_informations[0][0],"STR-0001541")
        # check that the last listing in the html_list is a "Private Room"
        self.assertEqual(listing_informations[-1][1],"Private Room")
        # check that the third listing has one bedroom
        self.assertEqual(listing_informations[2][-1],1)

    def test_get_detailed_listing_database(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save it to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # check that we have the right number of listings (20)
        self.assertEqual(len(detailed_database), 20)
        for item in detailed_database:
            # assert each item in the list of listings is a tuple
            self.assertEqual(type(item), tuple)
            # check that each tuple has a length of 6
            self.assertEqual(len(item), 6)
        # check that the first tuple is made up of the following:
        self.assertEqual(detailed_database[0], ('Loft in Mission District', 210, '1944564', '2022-004088STR', 'Entire Room', 1))
        # check that the last tuple is made up of the following:
        self.assertEqual(detailed_database[-1], ('Guest suite in Mission District', 238, '32871760', 'STR-0004707', 'Entire Room', 1))

    def test_write_csv(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call write csv on the variable you saved
        write_csv(detailed_database, "test.csv")
        # read in the csv that you wrote
        csv_lines = []
        with open(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.csv'), 'r') as f:
            csv_reader = csv.reader(f)
            for i in csv_reader:
                csv_lines.append(i)
        # check that there are 21 lines in the csv
        self.assertEqual(len(csv_lines), 21)
        # check that the header row is correct
        self.assertEqual(csv_lines[0], ['Listing Title', 'Cost', 'Listing ID', 'Policy Number', 'Place Type', 'Number of Bedrooms'])
        # check that the next row is Private room in Mission District,82,51027324,Pending,Private Room,1
        self.assertEqual(csv_lines[1], ['Private room in Mission District','82', '51027324', 'Pending', 'Private Room', '1'])
        # check that the last row is Apartment in Mission District,399,28668414,Pending,Entire Room,2
        self.assertEqual(csv_lines[-1], ['Apartment in Mission District','399', '28668414', 'Pending', 'Entire Room', '2'])

    def test_check_policy_numbers(self):
        # call get_detailed_listing_database on "html_files/mission_district_search_results.html"
        # and save the result to a variable
        detailed_database = get_detailed_listing_database("html_files/mission_district_search_results.html")
        # call check_policy_numbers on the variable created above and save the result as a variable
        invalid_listings = check_policy_numbers(detailed_database)
        # check that the return value is a list
        self.assertEqual(type(invalid_listings), list)
        # check that there is exactly one element in the string
        self.assertEqual(len(invalid_listings), 1)
        # check that the element in the list is a string
        self.assertEqual(type(invalid_listings[0]), str)
        # check that the first element in the list is '16204265'
        self.assertEqual(invalid_listings[0],'16204265')
    
    def test_extra_credit(self):
        self.assertTrue(extra_credit('1944564'))
        self.assertFalse(extra_credit('16204265'))

if __name__ == '__main__':
    database = get_detailed_listing_database("html_files/mission_district_search_results.html")
    write_csv(database, "airbnb_dataset.csv")
    check_policy_numbers(database)
    unittest.main(verbosity=2)
