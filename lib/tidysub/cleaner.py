#!/usr/bin/env python
# -*- coding: utf-8 -*-
import codecs
import re
from datetime import timedelta
from datetime import datetime
from regex import strings
from sickbeard import logger


#Definition of the TidySub class
class TidySub:
    """Load the subtitle, the file containing regex for removal
    and perform the cleaning and formatting actions"""
 
     
    def __init__(self, path_to_sub):

        #Boolean to stock if file is loaded
        self._is_file_loaded = False
               
        #Path to the subtitles file
        if re.match(r'^.+\.srt$', path_to_sub, re.UNICODE):
            self._path_to_sub = path_to_sub
        else:
            logger.log("TidySub : TidySub only corrects .srt files", logger.DEBUG)
            return

        self._team_list = list()
        self._sub_list = list()
        
        #Load the subtitles file
        self._sub_list = self._load_file(self._path_to_sub, True)
        if self._sub_list is not None:
            logger.log("TidySub : INFO: Subtitles file loaded", logger.DEBUG)

        return
        

    #Load a text file into a list in utf8
    def _load_file(self, path_to_file, removeEOL=False):

        try:
            fileToRead = codecs.open(path_to_file, "r", "latin-1")

        except IOError:
            logger.log("TidySub : File does not exist or sub is in mkv", logger.DEBUG)
            return
        except:
            try:
                fileToRead = codecs.open(path_to_file, "r", "utf-8")
            except:
                logger.log("TidySub : File not encoded in UTF-8 neither in latin-1", logger.DEBUG)
                return
            return
        tempList = list ()
        self._is_file_loaded = True

        #If the EOL must be removed
        if removeEOL:
            for i in fileToRead:
                tempList.append(i.rstrip('\n\r'))
        else:
            for i in fileToRead:
                tempList.append(i)
                
        fileToRead.close()
        
        return tempList

    #Write a file
    def _write_file(self, path_to_file, toWrite):

        if not self._is_file_loaded:
            logger.log("TidySub : No subtitles file was loaded", logger.DEBUG)
            return
                
        fileDest = codecs.open(path_to_file, "w", "latin-1")

        for i in toWrite:
            fileDest.write(i)

        fileDest.close()
        logger.log("TidySub : INFO: Subtitles file saved", logger.DEBUG)


    #Try to detect subtitles language
    def _detect_language(self, path_to_sub):
                
        if not self._is_file_loaded:
            logger.log("TidySub : No subtitles file was loaded", logger.DEBUG)
            return
        
        if re.match("^.+\.[a-z]{2}\.srt$", path_to_sub.lower(), re.UNICODE):
            path_to_sub = re.sub(r'\.[a-z]+$', '', path_to_sub.lower())
            return path_to_sub[len(path_to_sub)-2:len(path_to_sub)]
        else:
            return self._guess_language()

        
    def _guess_language(self):

        if not self._is_file_loaded:
            logger.log("TidySub : No subtitles file was loaded", logger.DEBUG)
            return

        #combine words into one regex string
        _french = "(^|[ ])" + "((" + ")|(".join(strings.get_guess_french(),True) + "))" + "([ ]|$)"
        _english = "(^|[ ])" + "((" + ")|(".join(strings.get_guess_english(),True) + "))" + "([ ]|$)"

        _count_french = 0
        _count_english = 0
        i = 0
        
        # Count the number of occurences of the words for each language
        while i < len(self._sub_list):
            
            if re.search(_french, self._sub_list[i].lower(), re.UNICODE):
                _count_french += 1
            if re.search(_english, self._sub_list[i].lower(), re.UNICODE):
                _count_english += 1
            
            i += 1

        #Return the language which has the highest count
        if _count_french > _count_english:
            logger.log("TidySub : INFO: Guessed language is French", logger.DEBUG)
            return "fr"
        elif _count_english > _count_french:
            logger.log("TidySub : INFO: Guessed language is English", logger.DEBUG)
            return "en"
        else:
            return "undefined"
        

    #Test Regex for team words
    def _clean_team(self):

        #combine team names into one regex string
        combined = "(" + ")|(".join(strings.get_teams()) + ")"

        i = 0
        
        while i < len(self._sub_list):
            
            if re.search(combined, self._sub_list[i], re.UNICODE):
                del self._sub_list[i]
                continue
            
            i += 1

    #Clean Hi in the subtitles file with regex
    def _clean_hi(self):

        i = 0
        
        while i < len(self._sub_list):
        
            #remove parentheses and content
            self._sub_list[i] = re.sub(r'\([^)]*\)', '', self._sub_list[i], re.UNICODE)
            
            #remove parentheses split in two lines
            if i < (len(self._sub_list) - 1) and re.match(r'^.*\(', self._sub_list[i], re.UNICODE) and not re.match(r'\)', self._sub_list[i], re.UNICODE) and re.match(r'^.*\)', self._sub_list[i+1], re.UNICODE):
                self._sub_list[i] = re.sub(r'\(.*$', '', self._sub_list[i], re.UNICODE)
                self._sub_list[i+1] = re.sub(r'^.*\)', '', self._sub_list[i+1], re.UNICODE)

            #remove brackets and content
            self._sub_list[i] = re.sub(r'\[[^)]*\]', '', self._sub_list[i], re.UNICODE)
            
            #remove brackets split in two lines
            if i < (len(self._sub_list) - 1) and re.match(r'^.*\[', self._sub_list[i], re.UNICODE) and not re.match(r'\]', self._sub_list[i], re.UNICODE) and re.match(r'^.*\]', self._sub_list[i+1], re.UNICODE):
                self._sub_list[i] = re.sub(r'\[.*$', '', self._sub_list[i], re.UNICODE)
                self._sub_list[i+1] = re.sub(r'^.*\]', '', self._sub_list[i+1], re.UNICODE)

            #remove braces and content
            self._sub_list[i] = re.sub(r'\{[^)]*\}', '', self._sub_list[i], re.UNICODE)

            #remove braces split in two lines
            if i < (len(self._sub_list) - 1) and re.match(r'^.*\{', self._sub_list[i], re.UNICODE) and not re.match(r'\}', self._sub_list[i], re.UNICODE) and re.match(r'^.*\}', self._sub_list[i+1], re.UNICODE):
                self._sub_list[i] = re.sub(r'\{.*$', '', self._sub_list[i], re.UNICODE)
                self._sub_list[i+1] = re.sub(r'^.*\}', '', self._sub_list[i+1], re.UNICODE)

            #remove name of speaker in front of the line
            self._sub_list[i] = re.sub(r'^[ \t]*[A-Z]+[ \t]*\:', '', self._sub_list[i], re.UNICODE)

            #remove leading and trailing spaces
            self._sub_list[i] = re.sub(r'^[ \t]+|[ \t]+$', '', self._sub_list[i], re.UNICODE)

            #remove multiple whitespaces
            self._sub_list[i] = re.sub(r'[ ]{2,}', ' ', self._sub_list[i], re.UNICODE)
            
            #Remove line with just a single hyphen
            self._sub_list[i] = re.sub(r'^\-$', '', self._sub_list[i], re.UNICODE)

            #delete empty balise
            self._sub_list[i] = re.sub(r'\<[^ ]+\>\<\/[^ ]+\>', '', self._sub_list[i], re.UNICODE)
        
            i += 1


    #French: Try to correct punctuation in the subtitles file with regex
    def _clean_punctuation_fr(self):
        
        i = 0
        
        while i < len(self._sub_list):
                   
            
            if not re.match(r'^[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+', self._sub_list[i]) and not re.match(r'^[0-9]+$', self._sub_list[i]):

                #remove leading and trailing spaces
                self._sub_list[i] = re.sub(r'^[ \t]+|[ \t]+$', '', self._sub_list[i], re.UNICODE)

                #remove multiple whitespaces
                self._sub_list[i] = re.sub(r'[ ]{2,}', ' ', self._sub_list[i], re.UNICODE)
                   
                #Correct comma
                if re.match("^.+ \,",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \,', ',', self._sub_list[i], re.UNICODE)
            
                if re.match("^.+\,[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\,(?!\")', ', ', self._sub_list[i], re.UNICODE)
                    
                #Correct semi-colon
                if re.match("^.*[^ ]+\;",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\;', ' ;', self._sub_list[i], re.UNICODE)
            
                if re.match("^.*\;[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\;', '; ', self._sub_list[i], re.UNICODE)
        
                #Correct colon
                if re.match("^.*[^ ]+\:",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\:', ' :', self._sub_list[i], re.UNICODE)
            
                if re.match("^.*\:[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\:(?!\")(?![0-9]+)', ': ', self._sub_list[i], re.UNICODE)
                
                #Correct dots
                if re.match("^.+ \.",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \.', '.', self._sub_list[i], re.UNICODE) 
            
                #if re.match("^.+\.[^ ]+",self._sub_list[i], re.UNICODE):
                #    self._sub_list[i] = re.sub(r'(?<=[A-Z]\.)\.(?!\")(?![A-Z]\.)', '. ', self._sub_list[i], re.UNICODE)
                    
                #Correct question mark
                if re.match("^.+[^ ]+\?",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\?', ' ?', self._sub_list[i], re.UNICODE)
        
                if re.match("^.+\?[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\?(?!\")', '. ', self._sub_list[i], re.UNICODE)
        
                #Correct exclamation mark
                if re.match("^.+[^ ]+\!",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\!', ' !', self._sub_list[i], re.UNICODE)
            
                if re.match("^.+\![^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\!(?!\")', '! ', self._sub_list[i], re.UNICODE)
                
                #Correct hyphen
                if re.match("^\-[^ ]",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'^\-', '- ', self._sub_list[i], re.UNICODE)
            
                
            
                #Correct not regular expressions
                self._sub_list[i] = re.sub(r'\? \!', '?!', self._sub_list[i], re.UNICODE)
                self._sub_list[i] = re.sub(r'\? \? \?', '???', self._sub_list[i], re.UNICODE)
                self._sub_list[i] = re.sub(r'\. \. \.', '...', self._sub_list[i], re.UNICODE)
                self._sub_list[i] = re.sub(r'\. \.', '..', self._sub_list[i], re.UNICODE)

                #remove leading and trailing spaces
                self._sub_list[i] = re.sub(r'^[ \t]+|[ \t]+$', '', self._sub_list[i], re.UNICODE)

                #remove multiple whitespaces
                self._sub_list[i] = re.sub(r'[ ]{2,}', ' ', self._sub_list[i], re.UNICODE)
                
                #remove space before closing balise
                if re.search(r' \<\/[^ ]+\>',self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \<\/', '</', self._sub_list[i], re.UNICODE)

                   
            i += 1


    #English: Try to correct punctuation in the subtitles file with regex
    def _clean_punctuation_en(self):
        
        i = 0
        
        while i < len(self._sub_list):
                   
            
            if not re.match(r'^[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+', self._sub_list[i]) and not re.match(r'^[0-9]+$', self._sub_list[i]):

                #remove leading and trailing spaces
                self._sub_list[i] = re.sub(r'^[ \t]+|[ \t]+$', '', self._sub_list[i], re.UNICODE)

                #remove multiple whitespaces
                self._sub_list[i] = re.sub(r'[ ]{2,}', ' ', self._sub_list[i], re.UNICODE)
                   
                #Correct comma
                if re.match("^.+ \,",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \,', ',', self._sub_list[i], re.UNICODE)
            
                if re.match("^.+\,[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\,(?!\")', ', ', self._sub_list[i], re.UNICODE)
                    
                #Correct semi-colon
                if re.match("^.* \;",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \;', ';', self._sub_list[i], re.UNICODE)
            
                if re.match("^.*\;[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\;', '; ', self._sub_list[i], re.UNICODE)
        
                #Correct colon
                if re.match("^.* \:",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \:', ':', self._sub_list[i], re.UNICODE)
            
                if re.match("^.*\:[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\:(?!\")(?![0-9]+)', ': ', self._sub_list[i], re.UNICODE)
                
                #Correct dots
                if re.match("^.+ \.",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \.', '.', self._sub_list[i], re.UNICODE)
            
                if re.match("^.+\.[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'(?<=[A-Z]\.)\.(?!\")(?![A-Z]\.)', '. ', self._sub_list[i], re.UNICODE)
                                        
                #Correct question mark
                if re.match("^.+ \?",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \?', '?', self._sub_list[i], re.UNICODE)
            
                if re.match("^.+\?[^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\?(?!\")', '. ', self._sub_list[i], re.UNICODE)
        
                #Correct exclamation mark
                if re.match("^.+ \!",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r' \!', '!', self._sub_list[i], re.UNICODE)
            
                if re.match("^.+\![^ ]+",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'\!(?!\")', '! ', self._sub_list[i], re.UNICODE)
                
                #Correct hyphen
                if re.match("^\-[^ ]",self._sub_list[i], re.UNICODE):
                    self._sub_list[i] = re.sub(r'^\-', '- ', self._sub_list[i], re.UNICODE)
            
                #Correct not regular expressions
                self._sub_list[i] = re.sub(r'\? \!', '?!', self._sub_list[i], re.UNICODE)
                self._sub_list[i] = re.sub(r'\? \? \?', '???', self._sub_list[i], re.UNICODE)
                self._sub_list[i] = re.sub(r'\. \. \.', '...', self._sub_list[i], re.UNICODE)
                self._sub_list[i] = re.sub(r'\. \.', '..', self._sub_list[i], re.UNICODE)

                #remove leading and trailing spaces
                self._sub_list[i] = re.sub(r'^[ \t]+|[ \t]+$', '', self._sub_list[i], re.UNICODE)

                #remove multiple whitespaces
                self._sub_list[i] = re.sub(r'[ ]{2,}', ' ', self._sub_list[i], re.UNICODE)
                                  
            i += 1

    #Remove music from line
    def _clean_music(self):

        i = 0
        
        while i < len(self._sub_list):

            if re.search(u'\u266a', self._sub_list[i], re.UNICODE):
                del self._sub_list[i]
                continue
            
            i += 1
    
    #Clean formatting
    #Remove blank lines
    #Test numbers
    #Formatting of time
    def _clean_formatting(self):

        #Remove unwanted blank lines
        self._clean_blank_lines()

        #Remove BOM character
        self._sub_list[0] = re.sub(u'\ufeff', '', self._sub_list[0], re.UNICODE)

        #Delete unnecessary lines
        i = 0
        count = 1
        while i < len(self._sub_list):

            j = 1

            #If the line is a number
            if re.match('^[0-9]+$', self._sub_list[i]):

                #First line must always be 1
                if i == 0:
                    self._sub_list[i] = str('1')
                    count = 1
                else:
                    self._sub_list[i] = str(count)

                #Exception if last line
                if i == len(self._sub_list)-1:
                    del self._sub_list[len(self._sub_list)-1]

                    if self._sub_list[len(self._sub_list)-1] == "":
                        del self._sub_list[len(self._sub_list)-1]
                    break
                
                #Check the second line
                #Check if it's a time range
                if re.match(r'^[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+', self._sub_list[i+1]):
                    self._clean_time_range(i+1)
                    j += 1

                    #Exception if last line
                    if (i+1) == len(self._sub_list)-1:
                        del self._sub_list[i+1]
                        continue
                    elif (i+2) == len(self._sub_list)-1:
                        break
                    elif (i+3) == len(self._sub_list)-1:
                        break
                  
                    #If the third line is empty and 4th is a number again
                    if self._sub_list[i+2] == "" and re.match('^[0-9]+$', self._sub_list[i+3]):
                        del self._sub_list[i]
                        del self._sub_list[i]
                        del self._sub_list[i]
                        continue
                    elif self._sub_list[i+2] == "" and not re.match('^[0-9]+$', self._sub_list[i+3]):
                        del self._sub_list[i+2]
                        continue

                    #if 3rd line is not empty
                    elif self._sub_list[i+3] == "" and not re.match('^[0-9]+$', self._sub_list[i+4]):
                        del self._sub_list[i+3]
                        continue
                    elif self._sub_list[i+3] == "" and re.match('^[0-9]+$', self._sub_list[i+4]):
                        j += 2
                    elif self._sub_list[i+3] is not "" and self._sub_list[i+4] == "" and not re.match('^[0-9]+$', self._sub_list[i+5]):
                        del self._sub_list[i+4]
                        continue
                    elif self._sub_list[i+3] is not "" and self._sub_list[i+4] is not "" and re.match('^[0-9]+$', self._sub_list[i+5]):
                        j += 3
                    elif self._sub_list[i+3] is not "" and self._sub_list[i+4] is not "" and self._sub_list[i+5] is not "" and re.match('^[0-9]+$', self._sub_list[i+6]):
                        j += 4

                    count += 1

                else:
                    logger.log("TidySub : Formatting error : timerange", logger.DEBUG)

            else:
                logger.log("TidySub : Formatting error : number line", logger.DEBUG)
                
            i += j

        #Re add the EOL character
        i = 0
        while i < len(self._sub_list)-1:
            self._sub_list[i] += '\r\n'
            i += 1

    #Remove unwanted blank lines in the subtitles file
    def _clean_blank_lines(self):
        
        #Remove a blank line if it is not before a number
        i = 0
        while i < len(self._sub_list)-1:
            if self._sub_list[i] == "" and  not re.match('^[0-9]+$', self._sub_list[i+1]):
                del self._sub_list[i]
                continue
            i += 1

        #Delete 1st line if blank
        if self._sub_list[0] == "":
            del self._sub_list[0]

        #Delete last line if blank
        if self._sub_list[len(self._sub_list)-1] == "":
            del self._sub_list[len(self._sub_list)-1]
        
        
    def _clean_time_format(self, string):
                
        if re.match(r'^[0-9]{2}\:[0-9]{2}\:[0-9]{2}\,[0-9]{3}$', string):
            return string

        else:
            #correct hours            
            if re.match(r'^[0-9]{1}\:', string):
                string = re.sub(r'^', '0', string, re.UNICODE)
                
            #correct minutes
            if re.match(r'^[0-9]{2}\:[0-9]{1}\:', string):
                string =  string[0:3] + "0" + string[3:len(string)]
            
            #correct seconds
            if re.match(r'^[0-9]{2}\:[0-9]{2}\:[0-9]{1}\,', string):
                string =  string[0:6] + "0" + string[6:len(string)]
                
            #correct ms
            if re.match(r'^[0-9]{2}\:[0-9]{2}\:[0-9]{2}\,[0-9]{1}$', string):
                string =  string[0:9] + "00" + string[9:len(string)]
            
            if re.match(r'^[0-9]{2}\:[0-9]{2}\:[0-9]{2}\,[0-9]{2}$', string):
                string = string[0:9] + "0" + string[9:len(string)]
                
            return string
            

    #Try to correct the format of the time
    def _clean_time_range(self, i):
        
        if re.match(r'^[0-9]{2}\:[0-9]{2}\:[0-9]{2}\,[0-9]{3} \-\-\> [0-9]{2}\:[0-9]{2}\:[0-9]{2}\,[0-9]{3}$', self._sub_list[i]):
            return
        
        if re.match(r'^[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+\s\-\-\>\s[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+', self._sub_list[i]):
            _start = re.sub("\s\-\-\>\s[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+$",'', self._sub_list[i], re.UNICODE)
            _end = re.sub(r'\r\n','', self._sub_list[i], re.UNICODE)
            _end = re.sub("^[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+\s\-\-\>\s",'', _end, re.UNICODE)
            self._sub_list[i] = self._clean_time_format(_start) + " --> " + self._clean_time_format(_end)
 
  
    #Main function to clean subtitles
    def Clean(self, removeHi=False, removeTeam=False, removeMusic=False, correct_punctuation=False, force_language = ""):

        if not self._is_file_loaded:
            logger.log("TidySub : No subtitles file was loaded", logger.DEBUG)
            return
       
        #Try to determine the language of the file
        if not force_language:
            _language = self._detect_language(self._path_to_sub)
        else:
            _language = force_language

        #If the team strings must be removed
        if removeTeam:
            logger.log("TidySub : INFO: Removing teams names", logger.DEBUG)
            
            #Call the function
            self._clean_team()
        
        #If music strings must be removed
        if removeMusic:
            logger.log("TidySub : INFO: Removing lyrics", logger.DEBUG)
            self._clean_music()

        #If Hi must be removed
        if removeHi:
            logger.log("TidySub : INFO: Removing HI", logger.DEBUG)
            self._clean_hi() 

        #If punctuation must be corrected
        if correct_punctuation:
            if _language == "fr":
                logger.log("TidySub : INFO: Correcting punctuation (French)", logger.DEBUG)
                self._clean_punctuation_fr()
            elif _language == "en":
                logger.log("TidySub : INFO: Correcting punctuation (English)", logger.DEBUG)
                self._clean_punctuation_en() 

        #Clean the formatting before saving the subtitles
        self._clean_formatting()
        
        #Write file
        self._write_file(self._path_to_sub, self._sub_list)


    def Offset(self, _sign, _hour=0, _minute=0, _second=0, _ms=0):

        if not self._is_file_loaded:
            logger.log("TidySub : No subtitles file was loaded", logger.DEBUG)
            return
        
        _correct = True
        
        # Check consistency of the parameters
        if _sign is not "+" and _sign is not "-":
            logger.log("TidySub : Bad sign for offset", logger.DEBUG)
            _correct = False
            
        if (not isinstance(_hour, int)) or _hour < 0 or _hour > 5:
            logger.log("TidySub : Hour is not correct for offset", logger.DEBUG)
            _correct = False
            
        if (not isinstance(_minute, int)) or _minute < 0 or _minute >= 60:
            logger.log("TidySub : Minute is not correct for offset", logger.DEBUG)
            _correct = False
        
        if (not isinstance(_second, int)) or _second < 0 or _second >= 60:
            logger.log("TidySub : Second is not correct for offset", logger.DEBUG)
            _correct = False
        
        if (not isinstance(_ms, int)) or _ms < 0 or _ms >= 1000:
            logger.log("TidySub : Milisecond is not correct for offset", logger.DEBUG)
            _correct = False

        if not _correct:
            return False
        
        #Save time to offset into a timedelta
        _time_offset = timedelta(hours=_hour, minutes=_minute, seconds=_second, microseconds=(_ms*1000))
        
        i = 0

        while i < len(self._sub_list):        
            
            if re.match(r'^[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+\s\-\-\>\s[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+', self._sub_list[i]):

                #remove EOL
                self._sub_list[i] = re.sub(r'\r\n$', '', self._sub_list[i], re.UNICODE)
                
                #Extract start time and save in timedelta
                _time_start = datetime.strptime('01/01/10 ' + re.sub(r' \-\-\> [0-9]+\:[0-9]+\:[0-9]+\,[0-9]+$', '', self._sub_list[i], re.UNICODE), '%d/%m/%y %H:%M:%S,%f')
                
                #Extract end time and save in timedelta
                _time_end = datetime.strptime('01/01/10 ' + re.sub(r'^[0-9]+\:[0-9]+\:[0-9]+\,[0-9]+\s\-\-\>\s', '', self._sub_list[i], re.UNICODE), '%d/%m/%y %H:%M:%S,%f')
                
                #Calculate the new time
                if _sign == "+":
                    _time_start += _time_offset
                    _time_end += _time_offset
                
                elif _sign == "-":
                    _time_start -= _time_offset
                    _time_end -= _time_offset
                    
                #create the new time range line
                self._sub_list[i] = str(_time_start.hour) + ":" + str(_time_start.minute) + ":" + str(_time_start.second) + "," + str(_time_start.microsecond/1000) + " --> " + \
                    str(_time_end.hour) + ":" + str(_time_end.minute) + ":" + str(_time_end.second) + "," + str(_time_end.microsecond/1000)
                
                #correct the time range line format
                self._clean_time_range(i)
                
                #re add EOL
                self._sub_list[i] += '\r\n'
            
            i += 1

        #Write the new SRT file
        self._write_file(self._path_to_sub, self._sub_list)
