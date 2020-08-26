import os
import sqlite3
from pathlib import Path

def getdatabases(dirpath):
    databases = []
    for x in os.listdir(dirpath):
        if (os.path.isdir(dirpath+"\\"+x)):
            if(getdatabases(dirpath+"\\"+x)!=[]):
                databases.append(getdatabases(dirpath+"\\"+x))
              
        elif(os.path.isfile(dirpath+"\\"+x)):
            try:
                
                cursor = sqlite3.connect(dirpath+"\\"+x)
                cursor.execute("select * from tables")

                    
                    
            except Exception as perror:
                
                if(str(perror) == "file is not a database"):
                    continue
                elif((str(dirpath)+"\\"+x).endswith("-journal")==False and Path(str(dirpath)+"\\"+x).stat().st_size != 0):
                    
                    databases.append(str(dirpath+"\\"+x))
                    
        
    return databases


dizinyolu = str(input("LÜTFEN ARAŞTIRMAK İSTEDİĞİNİZ DİZİNİN YOLUNU GİRİNİZ: "))
raporyolu = str(input("LÜTFEN RAPORU OLUŞTURMAK İSTEDİĞİNİZ YOLU GİRİNİZ(DOSYA ADI VE UZANTISI İLE BİRLİKTE): "))
dbs = getdatabases(dizinyolu)

def ayristir(alldbs,ayrilar):
    
    for i in alldbs:
        
        if(type(i) == str):
            ayrilar.append(i)
        else:
            ayristir(i,ayrilar)
    return ayrilar

ayrilar = []
ayridbs = ayristir(dbs,ayrilar)
dikt = {}
def getTableNames(ayridbs,dikt):    
    for i in ayridbs:
        
        temp = []
        connection = sqlite3.connect(i)
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tablenames = cursor.fetchall()
        for table in tablenames:
            temp.append(table[0])
            
        dikt[i] = temp
    
#BURADA DİKT DEĞİŞKENİNEN JSON BİR ŞEKİLDE TABLO ADLARI ATILDI.
getTableNames(ayridbs,dikt)


def gereksizlerisil(dikt,ayridbs):
    for i in ayridbs:
        try:
            dikt[i].remove('android_metadata')
        except Exception as ex:
            pass
        try:
            dikt[i].remove('meta')
        except Exception as ex:
            pass
        try:
            dikt[i].remove('sqlite_sequence')
        except Exception as ex:
            continue
    
    
        
gereksizlerisil(dikt,ayridbs)



def raporyaz(dikt,ayridbs):
    tam_text = ""    
    for dbpath in ayridbs:
        paragraf = ""
        tablenames = dikt[dbpath]
        tablesstr = ""
        for j in tablenames:
            tablesstr = tablesstr+j+", "
        if(tablesstr!=""):
            paragraf = "Dosya sisteminde "+dbpath+" konumundaki bu veritabanında "+tablesstr+" tablolari bulunmaktadır.\n\n"
            paragraf = paragraf.replace(",  ","  ")
            tam_text = tam_text + paragraf
    return tam_text

raport = raporyaz(dikt,ayridbs)

def ornekcek(dikt,ayridbs):
    rapor = ""
    for db in ayridbs:
        tablenames = dikt[db]
        connection = sqlite3.connect(db)
        cursor = connection.cursor()
        rapor = rapor+str(db)+" konumunda bulunan bu veri tabanındaki tablolar ve her tablo verisinin bir satır örneği aşağıdaki gibidir.\n\n"
        for table in tablenames:
            columnnames = []
            cursor.execute("PRAGMA table_info("+table+")")
            mytuplecolumns = cursor.fetchall()
            for k in mytuplecolumns:
                columnnames.append(k[1])
            
            cursor.execute("select * from "+str(table)+" LIMIT 0,1")
            firstrow = cursor.fetchall()
            try:
                firstrow1 = list(firstrow[0])
            
                try:
                    for i in (firstrow1):
                        if(type(i)== bytes):
                            firstrow1.remove(i)
                except Exception as index:
                    pass
            except Exception as ex:
                pass    
            rapor = rapor+"Tablo adı : "+str(table)+"\n\n"
            rapor = rapor+"Kolon isimleri : \n"+str(columnnames)+"\n\n"    
            rapor = rapor+"ilk satırdaki veriler : \n"+(str(firstrow1))+"\n\n\n\n"
    return rapor


raporson = ornekcek(dikt,ayridbs)
print(type(raporson))

with open(raporyolu,"w",encoding="utf-8") as raportxt:
    raportxt.write(raporson)
