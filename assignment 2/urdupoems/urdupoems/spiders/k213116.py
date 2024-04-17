import scrapy
import time
import re
import pandas as pd

class UrduSpider(scrapy.Spider):
    name = "K213116urdupoemsspider"
    start_urls = ['https://www.rekhta.org/poets?lang=ur']
    

    def __init__(self):
        self.ghazal_data = []  # Initialize an empty list to store ghazal data
        self.label = []
        self.count =1


    # Function to get the names and the links of Poets
    def parse(self, response):
        
        for i in range(1, 150):

            
            
            list_work = response.xpath(f'//*[@id="content"]/div/div/div/div[3]/div/div[5]/div/div[1]/div[{i}]/div/div[2]/div[2]/a/@title').getall()

            print("-----------------------.",list_work)

            # Check if Ghazal is in it.
            substring = "غزل"
            
            found = any(substring in s for s in list_work)    

            if not found:
                continue

            name = response.xpath(f'//*[@id="content"]/div/div/div/div[3]/div/div[5]/div/div[1]/div[{i}]/div/div[2]/div[1]/a/@title').get()
            poet_link = response.xpath(f'//*[@id="content"]/div/div/div/div[3]/div/div[5]/div/div[1]/div[{i}]/div/div[2]/div[1]/a/@href').get()


            extra = '/ghazals'

            # Split the string based on '?'
            parts = poet_link.split('?')

            # Concatenate '/ghazals' to the first part of the split string
            ghazal_link = parts[0] + '/ghazals'

            # If there are query parameters after '?', append them to the new URL
            if len(parts) > 1:
                ghazal_link += '?' + parts[1]

            

            print("----------------",name)
            print("----------------",ghazal_link)

            # Follow each poet link and pass control to parse_poet method
            yield response.follow(ghazal_link, callback=self.parse_poet, meta={'name': name, 'page_url': response.url})


    #Once the poet has been found and after clicking on his link. We will search through his GHAZAL
    def parse_poet(self, response):
        name = response.meta['name']
        page_url = response.meta['page_url']
        
        # Implement scraping logic for the poet's page here
        num_ghazals = len(response.css("div.contentListItems.nwPoetListBody").getall())+1

        for i in range(1,num_ghazals):
            link_ghazal = response.xpath(f'//*[@id="content"]/div/div[2]/div[5]/div[{i}]/a[2]/@href').get()
            
            if not link_ghazal:
                link_ghazal = response.xpath(f'//*[@id="content"]/div/div[2]/div[4]/div[{i}]/a[2]/@href').get()

                if not link_ghazal:
                    continue
                

            print(name,"------>",link_ghazal,"\n")

            

            yield response.follow(link_ghazal, callback=self.scrape_ghazal, meta={'name': name, 'page_url': response.url})



        # print("TEXT:    ",text)
        # After scraping, navigate back to the previous page
        yield response.follow(page_url, callback=self.parse)

    # After clicking on the ghazal, we will be scaping the urdu text of it        
    def scrape_ghazal(self,response):
        
        start=1
        ghazal = []
        page_url = response.meta['page_url']
        

        while(1):
            words = response.xpath(f'//p[@data-l="{start}"]//text()').getall()

            if not words:
                break

            # remove english letters, and other junk

            # Define a regular expression pattern to match English characters, symbols, or numbers
            pattern = re.compile(r'[' 'a-zA-Z0-9!@#$%^&*()_+=\[{\]};:\'",.<>?]')

            # Filter out elements from the list that match the pattern
            filtered_list = [word for word in words if not pattern.search(word)]

            concatenated_text = ' '.join(filtered_list)
            reversed_text = concatenated_text

            # [::-1]

            ghazal.append(reversed_text+"|")

            start = start+1

        news = "".join(ghazal)
        self.label.append(f"Ghazal {self.count}")
        self.ghazal_data.append(news)
        self.count = self.count+1
        

        yield response.follow(page_url, callback=self.parse_poet)

        
    def close(self, reason):
        # Create or update the DataFrame with the collected ghazal data
        df = pd.DataFrame({'Ghazal No': self.label, 'Content': self.ghazal_data})
        # print(df)  # Print the DataFrame for testing
    
        df.to_csv("test1.csv")
    
