from fastapi import FastAPI
import json
import requests
import os
import datetime as dt
import pytz

my_secret1 = os.environ['refresh_token']
my_secret2 = os.environ['client_secret']
my_secret3 = os.environ['client_id']
app = FastAPI()


def call_to_string(time_str):

  time_format = "%H:%M:%S"
  time_obj = dt.datetime.strptime(time_str, time_format)
  current_date = dt.datetime.now().date()
  datetime_object = time_obj.replace(year=current_date.year,
                                     month=current_date.month,
                                     day=current_date.day)
  return datetime_object


def create_nextday_call(acces_token, item, time, start):

  url = "https://www.zohoapis.in/crm/v5/coql"

  payload = json.dumps({
      "select_query":
      "SELECT 'What_Id->Leads.Last_Name', Call_Start_Time FROM Calls WHERE (Call_Start_Time >= '"
      + start + "T00:00:00+05:30' AND Call_Start_Time <= '" + start +
      "T23:59:59+05:30') AND 'Who_Id->Contacts.Lead_Source' = " +
      item["source"] + " ORDER BY Call_Start_Time ASC "
  })
  headers = {
      'Content-Type':
      'application/json',
      'Authorization':
      'Zoho-oauthtoken ' + acces_token,
      'Cookie':
      '34561a6e49=e281fadb2969b66b5522dd2b50f2cf9f; JSESSIONID=1789DBE86FB0FFE67F94580C71E8AEEF; _zcsr_tmp=bb2aeed3-5725-4a43-a283-ad2d5e1890e3; crmcsr=bb2aeed3-5725-4a43-a283-ad2d5e1890e3'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  if ("data" not in response.text):
    make_call(items=item, days=start + "T10:00:00", acces_tokens=acces_token)
    return item
  response = json.loads(response.text)
  first_call = ((((
      response["data"][0]["Call_Start_Time"]).split("T"))[1]).split("+"))[0]
  timing = (call_to_string(first_call))
  if (timing.hour >= 10 and timing.minute >= 5):
    make_call(items=item, days=start + "T10:00:00", acces_tokens=acces_token)
    return item

  times = [i["Call_Start_Time"].split("T")[1] for i in response["data"]]
  i = 0
  time_format = "%H:%M:%S"
  time_string2 = times[i].split("+")[0]
  current_date = dt.datetime.now().date()
  time_object2 = dt.datetime.strptime(time_string2, time_format)
  datetime_object2 = time_object2.replace(year=current_date.year,
                                          month=current_date.month,
                                          day=current_date.day)

  while i < len(times) - 1:
    time_string1 = times[i].split("+")[0]
    time_string2 = times[i + 1].split("+")[0]
    time_format = "%H:%M:%S"
    time_object1 = dt.datetime.strptime(time_string1, time_format)
    time_object2 = dt.datetime.strptime(time_string2, time_format)
    current_date = dt.datetime.now().date()
    datetime_object1 = time_object1.replace(year=current_date.year,
                                            month=current_date.month,
                                            day=current_date.day)
    datetime_object2 = time_object2.replace(year=current_date.year,
                                            month=current_date.month,
                                            day=current_date.day)
    if ((datetime_object2 - datetime_object1).seconds // 60 >= 10):
      day = str(datetime_object1 + dt.timedelta(minutes=5)).split(" ")[0]
      call_time = (str(datetime_object1 +
                       dt.timedelta(minutes=5)).split(" ")[1]).split(".")[0]
      day = start + "T" + call_time
      print("2.0")
      make_call(item, day, acces_token)
      return item

    i = i + 1
    print(datetime_object2)

  if i == len(times) - 1:

    day = str(datetime_object2 + dt.timedelta(minutes=5)).split(" ")[0]
    call_time = str(datetime_object2 + dt.timedelta(minutes=5)).split(" ")[1]
    day = start + "T" + call_time
    print(day)
    url = "https://www.zohoapis.in/crm/v5/Calls"

    # payload = json.dumps({
    #   "data": [{
    #     "What_Id ": {
    #       "name": item["name"],
    #       "id": item["id"]
    #     },
    #     "Description": item["desc"],
    #     "Call_Duration": None,
    #     "Call_Type": "Outbound",
    #     "Call_Start_Time": day,
    #     "Subject": "Call scheduled with Pushan Agrawal"
    #   }]
    # })
    print(item["id"])
    payload = json.dumps({
        "data": [{
            "Who_Id": {
                "id": str(item["id"])
            },
            "Description": item["desc"],
            "Call_Start_Time": day[0:16] + ":00",
            "Subject": item["desc"],
            "Call_Type": "Outbound",
            "Outbound_Call_Status": "Scheduled",
            "Call_Purpose": " Product Demo ZCRM"
        }]
    })
    headers = {
        'Authorization':
        'Zoho-oauthtoken ' + acces_token,
        'Content-Type':
        'application/json',
        'Cookie':
        '34561a6e49=05e68ae6a7c2f7d782946ef8f4a221ad; _zcsr_tmp=90ec0566-e656-408a-9766-8b920f8f9f89; crmcsr=90ec0566-e656-408a-9766-8b920f8f9f89'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    print("vhbchv")


def make_call(items, days, acces_tokens):
  print(items, days[0:16] + ":00")
  url = "https://www.zohoapis.in/crm/v5/Calls"

  payload = json.dumps({
      "data": [{
          "Who_Id": {
              "id": items["id"]
          },
          "Description": items["desc"],
          "Call_Start_Time": days[0:16] + ":00",
          "Subject": items["desc"],
          "Call_Type": "Outbound",
          "Outbound_Call_Status": "Scheduled",
          "Call_Purpose": " Product Demo ZCRM"
      }]
  })
  print(payload)
  headers = {
      'Authorization': 'Zoho-oauthtoken ' + acces_tokens,
      'Content-Type': 'application/json',
      # 'Cookie':
      # '34561a6e49=05e68ae6a7c2f7d782946ef8f4a221ad; _zcsr_tmp=90ec0566-e656-408a-9766-8b920f8f9f89; crmcsr=90ec0566-e656-408a-9766-8b920f8f9f89'
  }

  response = requests.request("POST", url, headers=headers, data=payload)
  print(response.text)


def return_time(i, time):
  ist = pytz.timezone('Asia/Kolkata')
  start = (time - dt.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
  start = start.split(" ")[0] + "T" + start.split(" ")[1] + "+05:30"
  end = (dt.datetime.now(ist) +
         dt.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
  end = end.split(" ")[0] + "T" + end.split(" ")[1] + "+05:30"

  return 0


# Default root endpoint
@app.get("/")
async def root():
  # start = str(
  #   (dt.datetime.now() +
  #    dt.timedelta(minutes=325)).isoformat()).split(".")[0].split() + "+5:30"

  return {"message": "Hello world"}


@app.get("/")
# Example path parameter
@app.get("/name/{name}")
async def name(name: str):
  return {"message": f"Hello {name}"}


@app.post("/items/")
async def create_item(item: dict):
  ist = pytz.timezone('Asia/Kolkata')

  url = "https://accounts.zoho.in/oauth/v2/token?refresh_token=" + my_secret1 + "&grant_type=refresh_token&client_id=" + my_secret3 + "&client_secret=" + my_secret2

  payload = {}
  headers = {
      'Cookie':
      '6e73717622=94da0c17b67b4320ada519c299270f95; _zcsr_tmp=a44588b0-468b-4627-ba63-a0c7d0107488; iamcsr=a44588b0-468b-4627-ba63-a0c7d0107488'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  response = json.loads(response.text)
  acces_token = response["access_token"]
  if dt.datetime.now(ist).hour >= 21:
    ist = pytz.timezone('Asia/Kolkata')
    time = dt.datetime.now(ist) + dt.timedelta(minutes=1440)
    start = str(time).split(" ")[0]
    create_nextday_call(item=item,
                        acces_token=acces_token,
                        time=time,
                        start=start)
    print("next day")
    return item
  if dt.datetime.now(ist).hour <= 10:
    ist = pytz.timezone('Asia/Kolkata')
    time = dt.datetime.now(ist)
    start = str(time).split(" ")[0]
    create_nextday_call(item=item,
                        acces_token=acces_token,
                        time=time,
                        start=start)
    print("next day")
    print("today after 10")
    return item
  time = dt.datetime.now(ist)
  # start = (dt.datetime.now(ist) -
  # dt.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
  # start = start.split(" ")[0] + "T" + start.split(" ")[1] + "+05:30"
  # end = (dt.datetime.now(ist) +
  # dt.timedelta(minutes=5)).strftime('%Y-%m-%d %H:%M:%S')
  # end = end.split(" ")[0] + "T" + end.split(" ")[1] + "+05:30"
  start = str(time).split(" ")[0]

  url = "https://www.zohoapis.in/crm/v5/coql"

  payload = json.dumps({
      "select_query":
      "SELECT 'What_Id->Leads.Last_Name', Call_Start_Time FROM Calls WHERE (Call_Start_Time >= '"
      + start + "T00:00:00+05:30' AND Call_Start_Time <= '" + start +
      "T23:59:59+05:30') AND 'Who_Id->Contacts.Lead_Source' = " +
      item["source"] + " ORDER BY Call_Start_Time ASC"
  })
  headers = {
      'Content-Type':
      'application/json',
      'Authorization':
      'Zoho-oauthtoken ' + acces_token,
      'Cookie':
      '34561a6e49=e281fadb2969b66b5522dd2b50f2cf9f; JSESSIONID=1789DBE86FB0FFE67F94580C71E8AEEF; _zcsr_tmp=bb2aeed3-5725-4a43-a283-ad2d5e1890e3; crmcsr=bb2aeed3-5725-4a43-a283-ad2d5e1890e3'
  }

  response = requests.request("POST", url, headers=headers, data=payload)

  if ("data" not in response.text):
    # cretae call api
    start = (dt.datetime.now(ist) +
             dt.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
    start = start.split(" ")[0] + "T" + start.split(" ")[1]

    url = "https://www.zohoapis.in/crm/v5/Calls"

    payload = json.dumps({
        "data": [{
            "Who_Id": {
                "id": item["id"]
            },
            "Description": item["desc"],
            "Call_Start_Time": start,
            "Subject": item["desc"],
            "Call_Type": "Outbound",
            "Outbound_Call_Status": "Scheduled",
            "Call_Purpose": " Product Demo ZCRM"
        }]
    })
    headers = {
        'Authorization':
        'Zoho-oauthtoken ' + acces_token,
        'Content-Type':
        'application/json',
        'Cookie':
        '34561a6e49=05e68ae6a7c2f7d782946ef8f4a221ad; _zcsr_tmp=90ec0566-e656-408a-9766-8b920f8f9f89; crmcsr=90ec0566-e656-408a-9766-8b920f8f9f89'
    }
    print(payload)
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)
    return item

  else:
    response = json.loads(response.text)
    times = [i["Call_Start_Time"].split("T")[1] for i in response["data"]]
    # if int(times[-1].split(":")[0]) > 20 and int(times[-1].split(":")[1]) > 55:
    #   # schedule next day
    #   print("next day")

    if (1 == 1):
      i = 0
      while i < len(times) - 1:
        time_string1 = times[i].split("+")[0]
        time_string2 = times[i + 1].split("+")[0]
        time_format = "%H:%M:%S"
        time_object1 = dt.datetime.strptime(time_string1, time_format)
        time_object2 = dt.datetime.strptime(time_string2, time_format)
        current_date = dt.datetime.now().date()
        datetime_object1 = time_object1.replace(year=current_date.year,
                                                month=current_date.month,
                                                day=current_date.day)
        datetime_object2 = time_object2.replace(year=current_date.year,
                                                month=current_date.month,
                                                day=current_date.day)
        if ((datetime_object2 - datetime_object1).seconds // 60 >= 10):
          if ((datetime_object2 - dt.timedelta(minutes=5)) >=
              (dt.datetime.now() + dt.timedelta(minutes=330))
              and (datetime_object1 + dt.timedelta(minutes=5)) <=
              (dt.datetime.now() + dt.timedelta(minutes=330))):
            day = (str(dt.datetime.now(ist))).split(" ")[0]
            call_time = (str(dt.datetime.now(ist)).split(" ")[1]).split(".")[0]
            day = day + "T" + call_time
            make_call(item, day, acces_token)
            return item
          elif (datetime_object1 + dt.timedelta(minutes=5)) > (
              dt.datetime.now() + dt.timedelta(minutes=330)):

            day = str(datetime_object1 + dt.timedelta(minutes=5)).split(" ")[0]
            call_time = (
                str(datetime_object1 +
                    dt.timedelta(minutes=5)).split(" ")[1]).split(".")[0]
            day = day + "T" + call_time
            print("2.0")
            make_call(item, day, acces_token)
            return item

        i = i + 1
        print(datetime_object2)
      if int(times[-1].split(":")[0]) > 20 and int(
          times[-1].split(":")[1]) > 55:
        #   # schedule next day
        print("next day")
        return item
      if i == len(times) - 1:
        if i == 0:
          time_string1 = times[i].split("+")[0]
          time_format = "%H:%M:%S"
          time_object1 = dt.datetime.strptime(time_string1, time_format)
          current_date = dt.datetime.now().date()
          datetime_object2 = time_object1.replace(year=current_date.year,
                                                  month=current_date.month,
                                                  day=current_date.day)
          if (datetime_object2 + dt.timedelta(minutes=5)) <= (
              dt.datetime.now() + dt.timedelta(minutes=330)):

            start = (dt.datetime.now(ist) +
                     dt.timedelta(minutes=1)).strftime('%Y-%m-%d %H:%M:%S')
            start = start.split(" ")[0] + "T" + start.split(" ")[1]

            url = "https://www.zohoapis.in/crm/v5/Calls"

            payload = json.dumps({
                "data": [{
                    "Who_Id": {
                        "id": item["id"]
                    },
                    "Description": item["desc"],
                    "Call_Start_Time": start,
                    "Subject": item["desc"],
                    "Call_Type": "Outbound",
                    "Outbound_Call_Status": "Scheduled",
                    "Call_Purpose": " Product Demo ZCRM"
                }]
            })
            headers = {
                'Authorization':
                'Zoho-oauthtoken ' + acces_token,
                'Content-Type':
                'application/json',
                'Cookie':
                '34561a6e49=05e68ae6a7c2f7d782946ef8f4a221ad; _zcsr_tmp=90ec0566-e656-408a-9766-8b920f8f9f89; crmcsr=90ec0566-e656-408a-9766-8b920f8f9f89'
            }
            print(payload)
            response = requests.request("POST",
                                        url,
                                        headers=headers,
                                        data=payload)
            print(response.text)
            return item
          else:
            print(" ")

        day = str(datetime_object2 + dt.timedelta(minutes=5)).split(" ")[0]
        call_time = str(datetime_object2 +
                        dt.timedelta(minutes=5)).split(" ")[1]
        day = day + "T" + call_time
        print(day)
        url = "https://www.zohoapis.in/crm/v5/Calls"

        # payload = json.dumps({
        #   "data": [{
        #     "What_Id ": {
        #       "name": item["name"],
        #       "id": item["id"]
        #     },
        #     "Description": item["desc"],
        #     "Call_Duration": None,
        #     "Call_Type": "Outbound",
        #     "Call_Start_Time": day,
        #     "Subject": "Call scheduled with Pushan Agrawal"
        #   }]
        # })
        payload = json.dumps({
            "data": [{
                "Who_Id": {
                    "id": item["id"]
                },
                "Description": item["desc"],
                "Call_Start_Time": day,
                "Subject": item["desc"],
                "Call_Type": "Outbound",
                "Outbound_Call_Status": "Scheduled",
                "Call_Purpose": " Product Demo ZCRM"
            }]
        })
        headers = {
            'Authorization':
            'Zoho-oauthtoken ' + acces_token,
            'Content-Type':
            'application/json',
            'Cookie':
            '34561a6e49=05e68ae6a7c2f7d782946ef8f4a221ad; _zcsr_tmp=90ec0566-e656-408a-9766-8b920f8f9f89; crmcsr=90ec0566-e656-408a-9766-8b920f8f9f89'
        }

        response = requests.request("POST", url, headers=headers, data=payload)
        print(response.text)
        print("vhbchv")
  # else:
  #   while("data" in response.text):

  # response = json.loads(response.text)

  return item
