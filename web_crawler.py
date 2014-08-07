 #The Web Crawler

# Author: Shah Chintan & Shah Saurabh



import urllib, htmllib, formatter, sys, urlparse, time
import json as myjson

# importing the python code for url normalization. This file is downloaded from http://nikitathespider.com/python/rerp/
sys.path.append("C:\Python27\url_normalize")
import url_normalize

# importing the python code for robot parsing. This file is downloaded from http://url-normalize.googlecode.com/hg/url_normalize.py 
sys.path.append("C:\Python27\robotexclusionparser")
import robotexclusionparser

# creation of RobotParser object and a dictionary to cache information about whether a particular robots.txt is parsed previously or not.
MyRobotParser=robotexclusionparser.RobotExclusionRulesParser()
RobotTxtDict=dict()

# LinksExtractor class to derive a new HTML parser and define the functions for handling anchor tags and frame links.
class LinksExtractor(htmllib.HTMLParser):

   # save_baseURL function will save the domain name from the input url.
   # It captures the domain from the seed url or the home page so that every child link can have an absolute url.
   def save_baseUrl(self, myurl):
           thedomain = urlparse.urlparse(myurl).netloc
           self.completedomain= 'http://' + str(thedomain)
           
   def __init__(self, formatter) :        # class constructor
      htmllib.HTMLParser.__init__(self, formatter)  # base class constructor
      self.links = []        # create an empty list for storing hyperlinks


   #The following function is the anchor tag handler. It also handles the relative url and converts them into absolute url.
   def start_a(self, attrs) :  # override handler of <A ...>...</A> tags
      # process the attributes
      if len(attrs) > 0 :
         for attr in attrs :
            if attr[0] == "href" :         # ignore all non HREF attributes
                self.o = urlparse.urlparse(attr[1])
                if (self.o.scheme == 'http') | (self.o.scheme == 'https') | (self.o.scheme == 'ftp') | (self.o.scheme == 'ftps'):
                    pass
                    if self.o.netloc == '':
                        pass
                        if str.find(self.o.path,'www') == -1:
                                pass
                                if str.find(str(attr[1]),'('): pass
                                elif (str(attr[1]) == '#') | (attr[1][0] != '/') :
                                    tempurl='/'+str(attr[1])
                                    self.newurl = urlparse.urljoin(self.completedomain,tempurl)
                                    self.append_urlLink(self.newurl)
                                else:
                                    self.newurl = urlparse.urljoin(self.completedomain,attr[1])
                                    self.append_urlLink(self.newurl)
                        else:
                            self.append_urlLink(attr[1])
                    elif (str(self.o.netloc).split('.')[0] == 'www'):
                        self.append_urlLink(attr[1])

   #The following function is the frame tag handler. It also handles the relative url and converts them into absolute url.
   def start_frame(self,attrs):
      if len(attrs) > 0 :
         for attr in attrs :
            if attr[0] == "src" :      
                self.o = urlparse.urlparse(attr[1])
                if (self.o.scheme == 'http') | (self.o.scheme == 'https') | (self.o.scheme == 'ftp') | (self.o.scheme == 'ftps'):
                    pass
                    if self.o.netloc == '':
                        pass
                        if str.find(self.o.path,'www') == -1:
                                pass
                                if str.find(str(attr[1]),'('): pass
                                elif (str(attr[1]) == '#') | (attr[1][0] != '/') :
                                    tempurl='/'+str(attr[1])
                                    self.newurl = urlparse.urljoin(self.completedomain,tempurl)
                                else:
                                    self.newurl = urlparse.urljoin(self.completedomain,attr[1])
                                self.links.append(self.newurl)
                        else:
                            self.links.append(attr[1]) # save the link info in the list
                    elif (str(self.o.netloc).split('.')[0] == 'www'):
                        self.links.append(attr[1]) # save the link info in the list

   def append_urlLink(self,url): # append the url to the list of valid child urls
       if self.checkRobotTxt(url) == True:
           #print "true"
           self.links.append(url)
   
   def get_links(self) :     # return the list of extracted links
        return self.links

   def checkRobotTxt(self,url):  # check whether a particular url is allowed or disallowed for any agent.
       self.currentRobotUrl=self.completedomain + "/robots.txt"
       if(self.currentRobotUrl in RobotTxtDict):
             pass
             #print "Already parsed robot.txt"
       else:
          try:
             RobotTxtDict[self.currentRobotUrl]=10
             MyRobotParser.fetch(self.currentRobotUrl)
          except(urllib2.URLError, socket.timeout, UnicodeError, UnicodeDecodeError, UnicodeEncodeError):
             print ""
       if MyRobotParser.is_allowed("*",url) == False: print "false:" + str(url)
       return MyRobotParser.is_allowed("*",url)


format = formatter.NullFormatter()         # create default formatter
htmlparser = LinksExtractor(format)        # create new Html parser object


userinput= raw_input('Google Search: ')
numberOfPages= int(raw_input('n: '))
print "Start time:" + str(time.asctime(time.localtime(time.time())))
start = time.time()
userinput = urllib.urlencode ({'q':userinput})
response = urllib.urlopen ( 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=8&' + userinput ).read() #extract 1st 8 results from google search engine
json = myjson.loads ( response )
results = json [ 'responseData' ][ 'results' ]
RepeatedLinkCheckdict=dict()  # dictionary to check whether a link is repeated for crawling.
dictValue = 1

from collections import deque
initqueue = deque()           # This is the queue that will contain valid urls to be crawled, in Breadth First Search order.

for result in results:
    url = result['url']   
    normalUrl=url_normalize.url_normalize(url)
    if (normalUrl in RepeatedLinkCheckdict): pass   # If the current url is already crawled discard
    else:
      RepeatedLinkCheckdict[normalUrl]=dictValue
      dictValue=dictValue+1
      initqueue.append(url)
   

PageDataList=[]            # This list will store the content of the pages successfully crawled
LinksParsedInOrder=[]      # This list will store the successfully crawled links in the order they are crawled and the related statistical information
lengthOfQueue=len(initqueue)
outputData=''
UrlCode=0
i=-1
TotalSizeOfPagesDownloaded=0
while i<numberOfPages:
        i=i+1
        currentUrl=initqueue.popleft()
        try:
           data = urllib.urlopen(currentUrl)
           StringData=data.read()
           UrlCode=data.getcode()
           if data.info().type != 'text/html': # discard all the files except for text/html
              StringData=''
              continue
           htmlparser.save_baseUrl(currentUrl) # save the domain name of this url
           htmlparser.feed(StringData)      # parse the file saving the info about links
           htmlparser.close()
           links = htmlparser.get_links()   # get the valid hyperlinks list
        except (IOError,NameError,htmllib.HTMLParseError,UnicodeDecodeError,UnicodeEncodeError, UnicodeError):
           continue
        PageDataList.append(StringData)    # Store the content of this page into list
        outputData=currentUrl+" Time: " + str(time.asctime(time.localtime(time.time()))) + " Size: " + str(len(StringData)/1000) + "KB" + " Code: " + str(UrlCode)
        LinksParsedInOrder.append(outputData) # store this crawled link and its statistical info in the list
        TotalSizeOfPagesDownloaded=TotalSizeOfPagesDownloaded+len(StringData)
        j=0
        while(j<len(links)):             # append the hyperlinks in the queue to follow Breadth First Search Order
           normalUrl=url_normalize.url_normalize(links[j])
           if (normalUrl in RepeatedLinkCheckdict):pass   # If the current url is already crawled discard
           else:
               RepeatedLinkCheckdict[normalUrl]=dictValue  # add this url to the dictionary for future reference
               dictValue=dictValue+1
               initqueue.append(links[j]) 
               lengthOfQueue=lengthOfQueue+1
           j=j+1
        print i

print "End of Downloading:" + str(time.asctime(time.localtime(time.time())))
print "Copying Data in Files"
lname='E:\\PythonPractise\\output\\Links\\link.txt'
f=open(lname,'a')
i=0
while(i<len(LinksParsedInOrder)): # Store the list of successful links in a text file
   f.write(LinksParsedInOrder[i]+'\n')
   i=i+1
f.write("Total time consumed: "+str((time.time()-start)/60)+'\n')
f.write("Total " + str(len(LinksParsedInOrder)) + " Pages downloaded successfully with total size as: "+ str(TotalSizeOfPagesDownloaded/1000) + " KB")
f.close()

count=1
i=1
fname='E:\\PythonPractise\\output\\Data\\'+'data'+str(count)+'.txt'
f=open(fname,'a')
while(i<len(PageDataList)): # Store the content of successful pages in text files with content of 100 pages per text file
   if ((i%100) == 0):
      count=count+1
      fname='E:\\PythonPractise\\output\\Data\\'+'data'+str(count)+'.txt'
      f=open(fname,'a')
   f.write(PageDataList[i])
   i=i+1
f.close()
print "End time:" + str(time.asctime(time.localtime(time.time())))
print "total time: "+str((time.time()-start)/60)
print "Total Size of pages downloaded: " + str(TotalSizeOfPagesDownloaded/1000) + " KB"
print "Total " + str(len(LinksParsedInOrder)) + " Pages downloaded successfully"

