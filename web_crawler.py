import urllib, htmllib, formatter, sys, urlparse, time
import json as myjson
sys.path.append("C:\Python27\url_normalize")
import url_normalize

sys.path.append("C:\Python27\robotexclusionparser")
import robotexclusionparser

MyRobotParser=robotexclusionparser.RobotExclusionRulesParser()
RobotTxtDict=dict()

class LinksExtractor(htmllib.HTMLParser): # derive new HTML parser
   def save_baseUrl(self, myurl):
           thedomain = urlparse.urlparse(myurl).netloc
           self.completedomain= 'http://' + str(thedomain)
           
   def __init__(self, formatter) :        # class constructor
      htmllib.HTMLParser.__init__(self, formatter)  # base class constructor
      self.links = []        # create an empty list for storing hyperlinks

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
                                else:
                                    self.newurl = urlparse.urljoin(self.completedomain,attr[1])
                                self.append_urlLink(self.newurl)
                                #self.links.append(self.newurl)
                        else:
                            self.append_urlLink(attr[1])
                            #self.links.append(attr[1]) # save the link info in the list
                    elif (str(self.o.netloc).split('.')[0] == 'www'):
                        self.append_urlLink(attr[1])
                        #self.links.append(attr[1]) # save the link info in the list


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


   def append_urlLink(self,url):
       if self.checkRobotTxt(url) == True:
           #print "true"
           self.links.append(url)
   
   def get_links(self) :     # return the list of extracted links
        return self.links

   def checkRobotTxt(self,url):
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


format = formatter.NullFormatter()           # create default formatter
htmlparser = LinksExtractor(format)        # create new parser object


userinput= raw_input('Google Search: ')
numberOfPages= int(raw_input('n: '))
print "Start time:" + str(time.asctime(time.localtime(time.time())))
start = time.time()
userinput = urllib.urlencode ({'q':userinput})
response = urllib.urlopen ( 'http://ajax.googleapis.com/ajax/services/search/web?v=1.0&rsz=8&' + userinput ).read()
json = myjson.loads ( response )
results = json [ 'responseData' ][ 'results' ]
RepeatedLinkCheckdict=dict()
dictValue = 1

from collections import deque
initqueue = deque()

for result in results:
    url = result['url']   # was URL in the original and that threw a name error exception
    normalUrl=url_normalize.url_normalize(url)
    if (normalUrl in RepeatedLinkCheckdict): a=0
    else:
      RepeatedLinkCheckdict[normalUrl]=dictValue
      dictValue=dictValue+1
      initqueue.append(url)
   

PageDataList=[]
LinksParsedInOrder=[]
lengthOfQueue=len(initqueue)
i=-1
TotalSizeOfPagesDownloaded=0
while i<numberOfPages:
        i=i+1
        currentUrl=initqueue.popleft()
        try:
           data = urllib.urlopen(currentUrl)
           StringData=data.read()
           if data.info().type != 'text/html':
              StringData=''
              continue
           htmlparser.save_baseUrl(currentUrl)
           htmlparser.feed(StringData)      # parse the file saving the info about links
           htmlparser.close()
           links = htmlparser.get_links()   # get the hyperlinks list
        except (IOError,NameError,htmllib.HTMLParseError,UnicodeDecodeError,UnicodeEncodeError, UnicodeError):
          # print "IOError or NameError caught" + " " + currentUrl
           continue
        PageDataList.append(StringData)
        LinksParsedInOrder.append(currentUrl)
        TotalSizeOfPagesDownloaded=TotalSizeOfPagesDownloaded+len(StringData)
        j=0
        while(j<len(links)):
           normalUrl=url_normalize.url_normalize(links[j])
           if (normalUrl in RepeatedLinkCheckdict):a=0
           else:
               RepeatedLinkCheckdict[normalUrl]=dictValue
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
while(i<len(LinksParsedInOrder)):
   f.write(LinksParsedInOrder[i]+'\n')
   i=i+1
f.close()

count=1
i=1
fname='E:\\PythonPractise\\output\\Data\\'+'data'+str(count)+'.txt'
f=open(fname,'a')
while(i<len(PageDataList)):
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

