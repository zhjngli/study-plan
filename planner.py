import json
import datetime
import os.path
import sys

def get_json(fname):
  json_data = open(fname).read()
  return json.loads(json_data)

def date_of(s):
  return datetime.datetime.strptime(s, '%m/%d/%Y').date()

def iso_day(d):
   return {
     'M': 1,
     'T': 2,
     'W': 3,
     'R': 4,
     'F': 5,
     'S': 6,
     'U': 7,
   }[d]

def create_schedule(cal_fname, classes_fname, save_fname):
  classes = get_json(classes_fname)
  cal = get_json(cal_fname) 

  vacations = [(date_of(v["start"]), date_of(v["end"])) for v in cal["vacations"]]
  vacation_dates = []
  for v in vacations:
    start, end = v
    assert (end - start).days >= 0, "Invalid vacation date ranges: {0} - {1}".format(start, end)
    date = start
    vacation_dates.append(date)
    while (date != end):
      date += datetime.timedelta(days=1)
      vacation_dates.append(date)

  first_day_of_class = date_of(cal["start"])
  last_day_of_class = date_of(cal["end"])
  n_days = (last_day_of_class - first_day_of_class).days

  lectures = [[] for i in range(n_days)]
  lec_nums = {}
  for k in classes.keys():
    lec_nums[k] = 1

  date = first_day_of_class
  for i in range(n_days):
    for class_name, days in classes.items():
      iso_days = [iso_day(d) for d in days] 
      if date.isoweekday() in iso_days and date not in vacation_dates:
        # 22 characters of space for the class name
        # 8 characters of space for lecture
        # 5 characters of space for date
        lec = "Lec {0}".format(lec_nums[class_name])
        lectures[i].append(
          "{0:<22}{1:<8}{2:<5}".format(class_name, lec, date.strftime("%m/%d"))
        )
        lec_nums[class_name] += 1
    date += datetime.timedelta(days=1)

  study_schedule = [[] for i in range(n_days + 28)]
  for i, ls in enumerate(lectures):
    study_schedule[i + 1] += [l + " (Day)" for l in ls]
    study_schedule[i + 7] += [l + " (Week)" for l in ls]
    study_schedule[i + 28] += [l + " (Month)" for l in ls]

  with open(save_fname, 'w') as outfile:
    to_save = [{} for i in range(len(study_schedule))]
    date = first_day_of_class
    for lectures in study_schedule:
      if len(lectures) != 0:
        outfile.write("{0}\n".format(date.strftime("%m/%d")))
        for l in lectures:
          outfile.write("  {0}\n".format(l))
      date += datetime.timedelta(days=1)

if __name__ == '__main__':
  cal_fname = "calendar.json"
  classes_fname = "classes.json"

  save_fname = "study_schedule.txt"
  if len(sys.argv) > 1:
    save_fname = sys.argv[1]

  if os.path.isfile(save_fname):
    print("File {0} already exists.".format(save_fname))
  else:
    create_schedule(cal_fname, classes_fname, save_fname)
