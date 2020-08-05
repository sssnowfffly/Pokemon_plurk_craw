# -*- coding: utf-8 -*-

from pprint import pprint
from googleapiclient.discovery import build
from bs4 import BeautifulSoup
import os,re,requests

def lineNotifyMessage(token, msg):
	headers = {
		"Authorization": "Bearer " + token, 
		"Content-Type" : "application/x-www-form-urlencoded"
	}
	payload = {'message': msg}
	r = requests.post("https://notify-api.line.me/api/notify", 
					  headers = headers, params = payload)
	return r.status_code

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'credentials.json'

credentials = None
service = build('sheets', 'v4', credentials=credentials)

spreadsheet_id = 'your_spreadsheet'
ranges ='A:H'
majorDimension='ROWS' #是否橫列顯示
insert_data_option = 'INSERT_ROWS'
value_input_option = "USER_ENTERED"

token = 'your_token' #LINE的訊息TOKEN


##檢查是否有資料在裡面
request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, 
												   ranges=ranges)
response = request.execute()

checklist=[]
for i in response["valueRanges"][0]['values'][1:]:
	checklist.append(i[0]+"_"+i[3])
	
request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, 
															   ranges="特殊任務!A:E")
response = request.execute()
checklistwithmission=[]
for j in response["valueRanges"][0]['values'][1:]:
	checklistwithmission.append(j[4])

request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, 
															   ranges="訓練家對戰!A:E")
response = request.execute()
checklistwithtrainer=[]
for j in response["valueRanges"][0]['values'][1:]:
	checklistwithtrainer.append(j[4])
		
request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, 
															   ranges="支線任務通知!A:E")
response = request.execute()

checklistwithside=[]
for j in response["valueRanges"][0]['values'][1:]:
	checklistwithside.append(j[4])

request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, 
															  ranges="主線任務通知!A:E")
response = request.execute()
	
checklistwithmain=[]
for j in response["valueRanges"][0]['values'][1:]:
	checklistwithmain.append(j[0])

request = service.spreadsheets().values().batchGet(spreadsheetId=spreadsheet_id, 
															   ranges="一般任務通知!A:E")
response = request.execute()

checklistwithnormal=[]
for j in response["valueRanges"][0]['values'][1:]:
	checklistwithnormal.append(j[4])
		
		
	
####main#########################################################
u='https://www.plurk.com/m/u/psp_2020'
soup = BeautifulSoup(requests.get(u).text, 'html.parser')
soup.find_all(class_="plurk_content clearfix")
for i in soup.find_all(class_="plurk_content clearfix"):
	try:
		if re.search('Side Story',i.text):
			if re.search('任務條件',i.text):
				if i.text in checklistwithside:
					print('already in')
					continue
				else:
					print(i.text)
					sidelist=[]
					for j in i.find_all('b'):
						sidelist.append(re.sub("<b>|</b>","",str(j)))
					mission,people,win,time=sidelist
					mission=mission.replace('收件區','')
					win='Y幣'+win
					time=time.split('【時間截止至')[1].split('】')[0]
					value_range_body = {
						"values":[[mission,people,win,time,i.text]],
						"majorDimension": "ROWS"
					}
					request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, 
																	 range="支線任務通知!A:E",  
																	 insertDataOption=insert_data_option,
																	 body=value_range_body,
																	 valueInputOption=value_input_option
																	)
					response = request.execute()


					message = "【支線任務】\n"+mission +"\n　組隊人數："+people+"\n　任務獎勵："+win+"\n　截止日期："+time
					print(message)
					#lineNotifyMessage(token, message)				
				
			else:
				continue
		
		elif re.search('Main Story',i.text):
			print(i.text)
			if i.text not in checklistwithmain:
				value_range_body = {
					"values":[[i.text]],
							"majorDimension": "ROWS"
						}
				request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, 
																		 range="主線任務通知!A:A",  
																		 insertDataOption=insert_data_option,
																		 body=value_range_body,
																		 valueInputOption=value_input_option
																		)
				response = request.execute()
				
				message = "【主線任務】\n"+i.text
				print(message)
				lineNotifyMessage(token, message)
			else:pass
		
			
		elif i.find_all("img")[0]['src'].split('/')[3]== '88382f98815c7a1a32053d715b840fc2_w24_h24.png':
			if re.search('阿羅拉|伽勒爾|型態',i.text):
				Time,info,catchs=map(str,list(i.find_all('b')))
				Time=i.text.split('】https://')[0].split('【結束時間 ')[1]
				info=info.replace('<b>','').replace('</b>','')
				No  =info.split('No.')[1].split(' ')[0]

				check_point =Time+'_'+No
				if check_point in checklist:
					print('already in ')
					continue
				Pic =i.text.split('No.')[0].split('】')[1]
				Name=info.split('(')[0].split('No.')[1].split(' ')[1]
				Sex =i.text.split(')')[0].split('(')[1]
				Cond=catchs.replace('<b>','').replace('</b>','').replace('捕捉條件：','')
				
				Desc=i.text.split("捕捉條件")[0].split(info)[1]
				array=[Time,Pic,info,No,Name,Sex,Desc,Cond]
				print(array)
				
				value_range_body = {
					"values":[array],
					"majorDimension": "ROWS"
				}
				request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id, 
																 range=ranges,  
																 insertDataOption=insert_data_option,
																 body=value_range_body,
																 valueInputOption=value_input_option
																)
				response = request.execute()


				message = str(info) +" \n　捕捉條件： "+Cond+" \n　結束時間："+Time
				lineNotifyMessage(token, message)
				
			else:
				try:
					print(i.text)
					blist=[]
					for j in i.find_all("b"): 
						blist.append(re.sub("<b>|</b>|【|】|捕捉條件：","",str(j)))
					if len(blist)== 2 :
						Time,cond = blist
						Time=Time.replace('結束時間 ',"")
						No=i.text.split("No.")[1].split(" ")[0]
						Sex =i.text.split(')')[0].split('(')[1]
						Name=i.text.split(No+" ")[1].split("(")[0]
						print(Name,Sex,No)
						info="No."+No+" "+Name+"("+Sex+")"
						
						check_point =Time+'_'+No
						if check_point in checklist:
							print('already in ')
							continue

					else:
						Time,info,cond = blist
						Time=Time.replace('結束時間 ',"")
						No=info.split("No.")[1].split(" ")[0]
						check_point =Time+'_'+No
						
						if check_point in checklist:
							print('already in ')
							continue
							
						if re.search("♂|♀",info):
							Sex=info.split("(")[1].split(")")[0]
							Name=info.split(" ")[1].split("(")[0]
							
						else:
							Sex="-"
							Name=info.split(" ")[1]
							
					Pic =i.text.split('No.')[0].split('】')[1]
					Cond=i.text.split('捕捉條件：')[1]
					Desc=i.text.split("捕捉條件")[0].split(info)[1]
					
					array=[str(Time),Pic,info,str(No),Name,Sex,Desc,Cond]
					print(array)
					

				except Exception as e:
					print(e)
					print('-'*30)

				value_range_body = {
					"values":[array],
					"majorDimension": "ROWS"
				}
				request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id,
																 range=ranges,  
																 insertDataOption=insert_data_option,
																 body=value_range_body,
																 valueInputOption=value_input_option
																)
				response = request.execute()

				
				message = str(info) +" \n　捕捉條件： "+Cond+" \n　結束時間："+Time
				print(message)
				lineNotifyMessage(token, message)
				
		elif i.find_all("img")[0]['src'].split('/')[3]== '2debf47f1ceeb668f27ec9dfe3872979_w25_h25.png':
			print(i.text)
			if i.text in checklistwithmission:
				print('already in ')
				continue

			try:
				slist=[]
				for j in i.find_all("b"):
					slist.append(re.sub('<b>|</b>','',str(j)))				
				times,name,cond=slist
				desc=i.text.split(')')[1].split('條件：')[0]
				times=re.sub("【|】|結束時間 |：",'',times)
				cond=re.sub('條件：','',cond)

				value_range_body={
					"values":[[times,name,cond,desc,i.text]],
					"majorDimension": "ROWS"
				}
				request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id,
																	 range="特殊任務!A:D",  
																	 insertDataOption=insert_data_option,
																	 body=value_range_body,
																	 valueInputOption=value_input_option
																	)
				response = request.execute()
				
				message = "【特殊任務】\n"+name+" \n　條件　　："+cond+" \n　結束時間："+times
				print(message)
				lineNotifyMessage(token, message)
			except Exception as e:
				print('特殊任務出錯')
				print(e)
				print('-'*30)
				
		elif i.find_all("img")[0]['src'].split('/')[3]== '29226ae729ab04a18f479c61d70348bd_w24_h24.png':
			print(i.text)
			if i.text in checklistwithtrainer:
				print('already in ')
				continue
			try:
				clist=[]
				for j in i.find_all('b'):
					clist.append(re.sub('<b>|</b>','',str(j)))
				time,name,cond,win=clist
				times=re.sub("【|】|結束時間 |：",'',times)
				name=re.sub("【|】|-",'',name)
				cond=re.sub('勝利條件：','',cond)
				win=win.replace('x','')

				value_range_body={
						"values":[[times,name,cond,win,i.text]],
						"majorDimension": "ROWS"
					}
				request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id,
																		 range="訓練家對戰!A:E",  
																		 insertDataOption=insert_data_option,
																		 body=value_range_body,
																		 valueInputOption=value_input_option
																		)
				response = request.execute()

				message = "【訓練家對戰】\n"+name+"\n　勝利條件："+cond+"\n　結束時間："+times+'\n　獲勝獎勵：Y幣'+win+'枚'
				print(message)
				lineNotifyMessage(token, message)	 
				
			except Exception as e:
				print('訓練家出錯')
				print(e)
				print('-'*30)

	

		elif i.find_all("img")[0]['src'].split('/')[3]== '6afd1508f4863195663d54f9fc51c066_w25_h25.png':
			print(i.text)
			if i.text in checklistwitnormal:
				print('already in ')
				continue
			try:
				qlist=[]
				for j in i.find_all('b'):
					qlist.append(re.sub('<b>|</b>','',str(j)))
				title,people,no,win,times=qlist
				times=re.sub("【|】|結束時間 |：",'',times)
				win=win.replace('x','')

				value_range_body={
						"values":[[title,people,win,times,i.text]],
						"majorDimension": "ROWS"
					}
				request = service.spreadsheets().values().append(spreadsheetId=spreadsheet_id,
																		 range="一般任務通知!A:E",  
																		 insertDataOption=insert_data_option,
																		 body=value_range_body,
																		 valueInputOption=value_input_option
																		)
				response = request.execute()

				message = "【一般任務】\n"+title+'\n　獲勝獎勵：Y幣'+win+'枚'+"\n　結束時間："+times
				print(message)
				lineNotifyMessage(token, message)	 
				
			except Exception as e:
				print('一般任務出錯')
				print(e)
				print('-'*30)
		
		print('-'*30)   
	except Exception as e:
		print(e)
		print('-'*30)
	

