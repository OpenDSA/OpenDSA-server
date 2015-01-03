# Python
from icalendar import Calendar, Event
import json

#Django
from django.contrib.auth.models import User

# A+
from userprofile.models import UserProfile
from course.models import CourseInstance

# OpenDSA
from opendsa.models import Exercise, UserExercise, Module, UserModule, Books, BookModuleExercise, UserExerciseLog, UserButton, UserData, UserBook
from opendsa.statistics import is_authorized

# Django
from django.template.context import RequestContext
from django.contrib.auth.decorators import login_required
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import get_object_or_404, render_to_response
from django.http import HttpResponse, HttpResponseForbidden
from course.context import CourseContext
from collections import OrderedDict
from django.db.models import Q
from settings import STATIC_URL
import time
import datetime
import os

# For convenience we store the name of the course mapped to book number
course_name = {4: 'CS223', 5:'CS3114A', 6:'CS3114B'}

# Lists specific account IDs to ignore (includes instructor accounts and abandoned accounts)
# Book 4
#   - 20 - instructor account
#   - 40 - abandoned
#   - 41 - abandoned
#   - 42 - abandoned
#   - 43 - abandoned
#   - 45 - abandoned
#   - 54 - abandoned?, only completed 1 exercise
#   - 88 - test account
#   - 89 - test account
#   - 222 - abandoned
#   - 547 - has UserBook entry for CS223 and CS3114A, since he supposedly lives in Blacksburg and completed the sorting chapter which isn't part of the CS223 book, I'm removing him from the CS223 data and leaving him in CS3114A

# Book 5
#   - 30 - instructor account
#   - 510 - abandoned, 57 exercises completed (only 6 unique ones), 4 events, entirely load-ka
#   - 626 - abandoned
#   - 632 - not on class roster

# Book 6
#   - 29 - instructor
#   - 462 - abandoned / test
#   - 471 - abandoned / test
#   - 473 - abandoned / test
#   - 481 - abandoned (no module, exercise, event, or user data)
#   - 499 - abandoned
#   - 538 - has UserBook associations for both 5 and 6 but is in CS3114A (book 5)
#   - 592 - abandoned?, only completed 2 exercises
#   - 617 - no exercises (user registered and looked at the gradebook, that's it)
accounts_to_ignore = {4: [20, 40, 41, 42, 43, 45, 54, 88, 89, 222, 547], 5:[30, 510, 626, 632], 6:[29, 462, 471, 473, 481, 499, 538, 592, 617]}

# http://stackoverflow.com/questions/10482339/how-to-find-median
def median(mylist):
  if len(mylist) == 0:
    return ''

  sorts = sorted(mylist)
  length = len(sorts)
  if not length % 2:
    return (sorts[length / 2] + sorts[length / 2 - 1]) / 2.0
  return sorts[length / 2]

@staff_member_required
def work_distribution(request, book, bin_size):
  # Select all users of a given book, except staff accounts, the phantom (guest) account and abandoned accounts
  users = UserBook.objects.filter(book=book, user__is_staff=0).exclude(user__username='phantom').exclude(user__in=accounts_to_ignore[int(book)]).order_by('id').values_list('user_id', flat=True)
  users = [user for user in users]
  users.sort()

  # bin_size is in hours
  bin_size = int(bin_size)
  bin_time_conversion = float(1) / 3600
  
  bins = {}
  
  user_exercises = UserExercise.objects.filter(user__in=users, proficient_date__gt=datetime.date(2012, 1, 1)).order_by('proficient_date')
  
  # Base time is the first time proficiency was obtained on an exercise
  base_time = time.mktime(user_exercises[0].proficient_date.timetuple())
  
  for ue in user_exercises:
    sec_from_base = time.mktime(ue.proficient_date.timetuple()) - base_time
  
    # Calculate which bin the time belongs to and increment the bin count
    bin_num = int(sec_from_base * bin_time_conversion / bin_size)
    if bin_num not in bins:
      bins[bin_num] = 1
    else:
      bins[bin_num] += 1
  
  # Create the CSV directory if necessary
  if not os.path.exists('CSV'):
    os.mkdir('CSV')
  
  # Create a CSV file with the bin information
  with open('CSV/' + book + '_work_distribution' + str(bin_size) + 'hr_res.csv', 'w') as file:
    #file.writelines('Calculating a Threshold from Bins of Module Times,Bin size = %s seconds\n' % bin_size)
    file.writelines('Time (Hours),Number of Proficient Exercises Completed In Time Range\n')

    for bin_num in xrange(max(bins.keys()) + 1):
      bin_time = (bin_num + 1) * bin_size
      
      count = ''
      
      if bin_num in bins:
        count = bins[bin_num]
        
      file.writelines('%s,%s\n' % (bin_time, count))

  return render_to_response("developer_view/default_csv_view.html")

# TODO: This is SLOOOOWWWWW!!
@staff_member_required
def time_required(request, book):
  # Compute average for each exercise across all students who complete it
  # Compute average for each student across all exercises they computer

  # Select all users of a given book, except staff accounts, the phantom (guest) account and abandoned accounts
  users = UserBook.objects.filter(book=book, user__is_staff=0).exclude(user__username='phantom').exclude(user__in=accounts_to_ignore[int(book)]).order_by('id').values_list('user_id', flat=True)
  users = [user for user in users]
  users.sort()
  
  exer_order = OrderedDict()
  
  # Specify mini-slideshow order
  exer_order['ss'] = ["InssortCON1", "InssortCON2", "InssortCON3", "BubsortCON1", "BubsortCON2", "SelsortCON1", "SelsortCON2", "shellsortCON1", "shellsortCON2", "shellsortCON4", "shellsortCON5", "shellsortCON7", "shellsortCON9", "mergesortCON1", "mergeImplCON1", "mergeImplCON2", "QuicksortCON1", "heapsortCON", "BinsortCON1", "BinsortCON2", "hashIntroCON1", "hashFuncExCON1", "hashFuncExCON2", "buckethashCON1", "buckethashCON2", "linProbeCON1", "linProbeCON2", "collisionCON1", "collisionCON2", "collisionCON3", "collisionCON4", "collisionCON5", "collisionCON6", "collisionCON7", "collisionCON8", "hashdelCON1"]

  # Specify AV order
  exer_order['av'] = ["insertionsortAV", "bubblesortAV", "selectionsortAV", "shellsortAV", "mergesortAV", "quicksortAV", "QuicksortCON1", "heapsortCON", "BinsortCON1", "BinsortCON2", "radixLinkAV", "radixArrayAV"]

  # Specify proficiency exercise order
  exer_order['pe'] = ["ShellsortProficiency", "mergesortProficiency", "quicksortProficiency", "heapsortProficiency", "HashingDeleteProficiency"]

  # Specify calculator order
  exer_order['cc'] = ["Birthday", "MidSquare", "StringSimple", "StringSfold"]

  # Specify proficiency exercise order
  exer_order['ps'] = ["ShellsortPerformance"]

  # Specify mini-proficiency exercise order
  exer_order['mp'] = ["InssortPRO", "BubsortPRO", "SelsortPRO", "FindInversionsPRO", "ShellsortSublist", "ShellsortSeries", "MergesortPRO", "QuicksortPivotPRO", "QuicksortPartitPRO", "HeapsortPRO", "RadixsortPRO", "OpenHashPRO", "HashingBucketPRO", "HashingBucket2PRO", "HashingLinearProbePRO", "HashingLinearStepProbePRO", "HashingPseudoRandomProbePRO", "HashingQuadraticProbePRO", "HashingDoubleProbePRO"]

  # Specify KA (summary) exercise order
  exer_order['ka'] = ["SortIntroSumm", "InssortSumm", "BubsortSumm", "SelsortSumm", "SortCompareSumm", "ExchangeSumm", "ShellsortSumm", "MergesortSumm", "QuicksortSumm", "HeapsortSumm", "RadixSortSumm", "SortAlgCompSumm", "SortBoundSumm", "ChapterSumm", "HashFuncPROSumm", "HashFuncSumm", "HashAnalSumm", "HashDelSumm", "HashChapterSumm"]

  user_exercise_logs = UserExerciseLog.objects.filter(user__in=users).order_by('time_done').only('user', 'exercise', 'time_taken', 'earned_proficiency', 'count_attempts')

  exer_data = {}
  
  user_data = OrderedDict()

  for uel in user_exercise_logs:
    user = uel.user.id
    exer_name = uel.exercise.name
    time_taken = uel.time_taken

    # Initialize dictionary of exercises and exercise type lists for each user
    if user not in user_data:
      user_data[user] = {'ss': [], 'av': [], 'pe': [], 'cc': [], 'ps': [], 'mp': [], 'ka': []}

    # Initialize dictionary of stats for each exercise
    if exer_name not in user_data[user]:
      user_data[user][exer_name] = {'time_required': 0, 'proficient': False}

    # If the user is not yet proficient with the exercise we add the time taken by the exercise
    if not user_data[user][exer_name]['proficient']:
      # Correct time_taken, if necessary
      if time_taken > 1000000:
        # Since uel.count_attempts is the UIID which is a timestamp taken when the page loads which is equal to the value subtracted from the end time to calculate time_taken, we can approximate a corrected value
        time_taken = int(time_taken - uel.count_attempts / 1000)
        print 'Corrected time: ' + str(time_taken)
      
      # Increment the time required by the length of this instance
      user_data[user][exer_name]['time_required'] += time_taken

      if uel.earned_proficiency == 1:
        # Mark the exercise as proficient (stop counting the time for it)
        user_data[user][exer_name]['proficient'] = True
        
        time = user_data[user][exer_name]['time_required']
        
        # Record the total time required (associated with an exercise)
        if exer_name not in exer_data:
          exer_data[exer_name] = []
        
        exer_data[exer_name].append(time)
        
        # Record the total time required (associated with the user's appropriate exercise type list)
        for exer_type in exer_order:
          if exer_name in exer_order[exer_type]:
            user_data[user][exer_type].append(time)
            break

  # Create the CSV directory if necessary
  if not os.path.exists('CSV'):
    os.mkdir('CSV')

  with open('CSV/' + book + '_time_required_by_student.csv', 'w') as file:
    file.write('Time (in seconds) Required by Student (' + course_name[int(book)] + ')\n')
    file.write('User,' + ','.join(exer_type.upper() + ' Median' for exer_type in exer_order.keys()) + '\n')

    for user in users:
      # Append the user ID and medians of each exercise type list to the file
      file.write(('%s,' % user) + ','.join(str(median(user_data[user][t])) if t in user_data[user] else '' for t in exer_order.keys()) + '\n')

  with open('CSV/' + book + '_time_required_by_exercise.csv', 'w') as file:
    file.write('Time (in seconds) Required By Exercise (' + course_name[int(book)] + ')\n\n')
    
    for exer_type in exer_order:
      file.write(','.join(exer_order[exer_type]) + '\n')
      file.write(','.join(str(median(exer_data[exer])) if exer in exer_data else '' for exer in exer_order[exer_type]) + '\n\n')

      # Print all of a students medians for all exercises (so additional processing can be done such as quartiles for a specific exercise or T-test on a specific exercise between classes)
      with open('CSV/' + book + '_time_required_student_vs_' + exer_type.upper() + '.csv', 'w') as sve:
        sve.write('Time (in seconds) Required -- Exercise vs Student (' + course_name[int(book)] + ')\n\n')
        sve.write('User,' + ','.join(exer for exer in exer_order[exer_type]) + '\n')
        
        for user in users:
          # Append the user ID and medians of each exercise type list to the file
          sve.write(('%s,' % user) + ','.join(str(user_data[user][exer]['time_required']) if exer in user_data[user] else '' for exer in exer_order[exer_type]) + '\n')

  return render_to_response("developer_view/default_csv_view.html")

def skipping_text(request, book):
  # Select all users of a given book, except staff accounts, the phantom (guest) account and abandoned accounts
  users = UserBook.objects.filter(book=book, user__is_staff=0).exclude(user__username='phantom').exclude(user__in=accounts_to_ignore[int(book)]).order_by('id').values_list('user_id', flat=True)
  users = [user for user in users]
  users.sort()

  # Amount of time in each bin (in seconds)
  bin_size = 5 # seconds
  threshold = 30 # seconds
  # Keep a count of the total number of module times counted (so we can calculate quartiles)
  total_num_module_times = 0

  # A dictionary where each key is a bin and each value is the number of modules whose time is within the given bin
  module_time_bins = {}

  # A dictionary where each key is a user and each value is a dictionary of modules whose values are the time the user spent from page load to the first exercise event
  user_info = OrderedDict()

  for user in users:
    user_info[user] = {}

    # Get the user's event data, specifically page load and unload events and showhide button events
    user_buttons = UserButton.objects.filter(user=user, book=book).filter(Q(name__contains='_showhide_btn') | Q(name='document-ready') | Q(name='window-unload')).order_by('action_time')

    # Dictionary used to keep track of the total time a user spends on a module page (in case they load the page several times before clicking on an exercise)
    module_time = {}

    print 'user: ' + str(user)

    # Loop through events, the first time a module is loaded, look ahead for a showhide button before the matching window unload event
    for i in xrange(len(user_buttons)):
      ub = user_buttons[i]

      # If the event is a module load and the current user does not have a time for this module...
      if ub.name == 'document-ready' and ub.module not in user_info[user].keys():
        #print '  load module: ' + str(ub.module.name) + ', time: ' + str(time.mktime(ub.action_time.timetuple()))

        # Initialize the time spent on the module
        if ub.module not in module_time:
          module_time[ub.module] = 0

        # Look ahead for an unload event or showbutton event
        for j in xrange(i, len(user_buttons)):
          ub2 = user_buttons[j]

          # Calculate the number of seconds from module load event to current event
          num_seconds = time.mktime(ub2.action_time.timetuple()) - time.mktime(ub.action_time.timetuple())

          if ub2.name == 'window-unload' and ub2.module == ub.module:
            # If the module was unloaded, keep a running total of the time spent on the module
            module_time[ub.module] += num_seconds

            #print '    unload module: ' + str(ub.module.name) + ', time: ' + str(time.mktime(ub2.action_time.timetuple())) + ', total time: ' + str(module_time[ub.module])

            break
          elif '_showhide_btn' in ub2.name and ub2.module == ub.module:
            # Once an exercise event is detected, record the total time spent on the module
            num_seconds += module_time[ub.module]
            user_info[user][ub.module] = num_seconds

            #print '    exercise event at: ' + str(time.mktime(ub2.action_time.timetuple()))
            print '    time: ' + str(num_seconds)

            bin_num = int(num_seconds / bin_size)

            # Initialize / increment the count of the appropriate bin
            if bin_num in module_time_bins:
              module_time_bins[bin_num] += 1
            else:
              module_time_bins[bin_num] = 1

            total_num_module_times += 1

            break

  # Create the CSV directory if necessary
  if not os.path.exists('CSV'):
    os.mkdir('CSV')

  # Create a CSV file with the bin information
  with open('CSV/' + book + '_skipping_text_threshold.csv', 'w') as file:
    file.writelines('Calculating a Threshold from Bins of Module Times,Bin size = %s seconds\n' % bin_size)
    file.writelines('Time (Seconds),Number of Modules Whose Load-to-Exercise Time is Within Each Range\n')

    # Keep a count of the number of modules encountered, for comparison against quartiles
    count_mod_time = 0

    # Stores the time when each quartile is reached
    quartile_times = [0, 0, 0]

    for bin_num in xrange(max(module_time_bins.keys()) + 1):
      bin_time = (bin_num + 1) * bin_size

      if bin_num in module_time_bins:
        file.writelines('%s,%s\n' % (bin_time, module_time_bins[bin_num]))

        # Increment count by number of modules in bin
        count_mod_time += module_time_bins[bin_num]

        if quartile_times[0] == 0 and count_mod_time > (total_num_module_times / 4):
          quartile_times[0] = bin_time
        elif quartile_times[1] == 0 and count_mod_time > (total_num_module_times / 2):
          quartile_times[1] = bin_time
        elif quartile_times[2] == 0 and count_mod_time > (total_num_module_times * 3 / 4):
          quartile_times[2] = bin_time

      else:
        file.writelines('%s,0\n' % bin_time)

    file.writelines('\nQuartiles (%s second resolution)\n1st,2nd,3rd\n' % bin_size)
    file.writelines(','.join(str(t) + ' sec' for t in quartile_times))

  # Create a CSV file with the number of modules each student rushed through
  #with open('CSV/' + book + '_skipping_text_users_below_threshold.csv', 'w') as file:
  #  file.writelines('User,Number of Modules Below Threshold,Total Number of Modules\n')
  #
  #  # For each user, count the number of modules whose time is below the threshold
  #  for user in users:
  #    num_below_threshold = len([t for t in user_info[user].values() if t <= threshold])
  #    total = len(user_info[user])
  #    file.writelines('%s,%s,%s\n' % (user, num_below_threshold, total))

  return render_to_response("developer_view/default_csv_view.html")

@staff_member_required
def slideshow_stats(request, book):
  # Needs to count the total number of slideshows a student attempts, the number they complete, the number they cheat on and the average time

  # Select all users of a given book, except staff accounts, the phantom (guest) account and abandoned accounts
  users = UserBook.objects.filter(book=book, user__is_staff=0).exclude(user__username='phantom').exclude(user__in=accounts_to_ignore[int(book)]).order_by('id').values_list('user_id', flat=True)
  users = [user for user in users]
  users.sort()

  # Filter events to show only slideshow data
  ss_events_query = UserButton.objects.filter(book=book, name__in=['jsav-forward', 'jsav-backward', 'jsav-begin', 'jsav-end']).order_by('action_time')

  bin_size = 1 # seconds
  threshold = 1 # seconds
  avg_step_time_bins = {}
  median_bin_size = 0.5 # seconds
  median_time_bins = {}
  # Keep a count of the total number of slideshows times counted (so we can calculate quartiles)
  total_num_ss_times = 0

  # Create the CSV directory if necessary
  if not os.path.exists('CSV'):
    os.mkdir('CSV')

  with open('CSV/' + book + '_slideshow_stats.csv', 'w') as file:
    file.write('Slideshows Stats (' + course_name[int(book)] + ')\n')
    file.write('User,Total Attempted,Unique Attempted,Total Completed,Unique Completed,Number Rushed Through,Number of Slideshows Missing Some Event Data,Number of Slideshows Missing All Event Data,Total Number of Slideshows Missing Event Data,Skipped for Credit,Median Seconds Per Slide\n')

    for user in users:
      # Filter UserExerciseLog by user and slideshows where the user gained proficiency
      # Possible to also limit by a time threshold (to reduce the number of results that require processing, but then we can't determine the total number of completions (time_taken__lte=2)
      user_exercise_logs = UserExerciseLog.objects.filter(user=user, exercise__ex_type='ss', earned_proficiency=1).order_by('time_done').only('exercise', 'time_taken', 'count_attempts')

      # Initialize counters
      total_attempted = 0
      unique_attempted = 0
      total_completed = 0
      unique_completed = 0
      rushed_through = 0
      skipped_for_credit = 0
      num_missing_some_data = 0
      avg_time_per_step = 0

      # Used to keep track of exercises seen so we only calculate the average time per step for the first time a user completes the exercise
      exercises_seen = []

      # Keep track of times for each unique instance
      ss_time = {}

      # Initialize the total time for each unique instance using UserExerciseLog because its more accurate than calculating it from event data
      for uel in user_exercise_logs:
        uiid = uel.count_attempts
        exer = uel.exercise.id
        time_taken = uel.time_taken

        # Perform the following actions for all unique (exercise, uiid) pairs, allows different exercises with the same UIID such as mini-slideshows on the same module page and the same exercise with different UIIDs such as multiple attempts at the same exercise
        if (exer, uiid) not in ss_time.keys():
          # Count the total number of unique slideshow instances completed
          total_completed += 1

          # Correct time_taken, if necessary
          if time_taken > 1000000:
            # Since uel.count_attempts is the UIID which is a timestamp taken when the page loads which is equal to the value subtracted from the end time to calculate time_taken, we can approximate a corrected value
            time_taken = int(time_taken - uiid / 1000)
            print 'Corrected time: ' + str(time_taken)

          ss_time[(exer, uiid)] = time_taken

          if exer not in exercises_seen:
            # Count the number of unique slideshows completed
            unique_completed += 1
            exercises_seen.append(exer)

      # Reset list of exercises
      exer_uiid_pairs_seen = set()
      exercises_seen = []
      uiids_seen = set()

      # List to keep track of average time per step of each exercise
      avg_times = []

      # Get all the event's for a specific user
      ss_events = ss_events_query.filter(user=user).values('uiid', 'exercise', 'description')

      for event in ss_events:
        exercise = event['exercise']

        # If the event belongs to a unique instance, denoted by a unique (exercise, uiid) pair...
        if 'uiid' in event and event['uiid'] != None and (exercise, event['uiid']) not in exer_uiid_pairs_seen:
          uiid = event['uiid']

          # Count the attempt
          total_attempted += 1
          exer_uiid_pairs_seen.add((exercise, uiid))

          # Increment the count of unique attempts if the exercise has not been seen before
          if exercise not in exercises_seen:
            unique_attempted += 1
            exercises_seen.append(exercise)

          # If the user obtained proficiency on this attempt
          if (exercise, uiid) in ss_time:
            # Determine if the user cheated on this instance

            # Parse the total number of slides from the description
            num_slides = int(event['description'].split(' / ')[1])

            # Get the descriptions of events from a specific exercise instance
            descriptions = ss_events_query.filter(user=user, exercise=exercise, uiid=uiid).values_list('description', flat=True)

            # If the last step (which triggers proficency) is logged, ensure all steps were logged
            if ' / '.join([str(num_slides)] * 2) not in descriptions:
              # If the last step wasn't logged, we know event data is missing because the user obtained proficiency which means they finished
              num_missing_some_data += 1
              #print 'Corrupt: (user: ' + str(user) + ', exer: ' + str(exercise) + ', uiid: ' +  str(uiid) + ')'

            # Ensure every slide (except the last) was viewed, we know they viewed the last because that's what triggers getting credit, allows a little bit more flexibility for dealing with corrupt data
            for i in xrange(1, num_slides):
              if ' / '.join([str(i), str(num_slides)]) not in descriptions:
                skipped_for_credit += 1
                print 'Cheated: (user: ' + str(user) + ', exer: ' + str(exercise) + ', uiid: ' +  str(uiid) + ')'
                break


            # Calculate average time spent on each slide
            if ss_time[(exercise, uiid)] == 0:
              avg_times.append(0)
            else:
              avg_step_time = ss_time[(exercise, uiid)] / float(num_slides)
              avg_times.append(avg_step_time)

              # Initialize / increment number of slideshows in the calculated bin
              bin_num = int(avg_step_time / bin_size)
              if bin_num in avg_step_time_bins:
                avg_step_time_bins[bin_num] += 1
              else:
                avg_step_time_bins[bin_num] = 1

              total_num_ss_times += 1

              # Increment number of slideshows rushed through if the normalized time is below the threshold
              if avg_step_time <= threshold:
                rushed_through += 1

      # Compute the median time per step for a user
      med_time = median(avg_times)

      # Place median times in bins
      if med_time != '':
        bin_num = int(med_time / median_bin_size)
        if bin_num in median_time_bins:
          median_time_bins[bin_num] += 1
        else:
          median_time_bins[bin_num] = 1

      # Calculate the number of proficient slideshows for which there is no event data at all
      missing_pairs = set(ss_time.keys()) - exer_uiid_pairs_seen
      num_missing_all_data = len(missing_pairs)

      #if num_missing_some_data > 0:
        #print 'ss_time: ' + str(keys)
        #print 'exer_uiid_pairs_seen: ' + str(pairs)
        #print 'diff: ' + str(missing_pairs)
        #print 'num_missing_some_data: ' + str(num_missing_some_data) + '\n\n\n'


      file.write(','.join(str(x) for x in [user, total_attempted, unique_attempted, total_completed, unique_completed, rushed_through, num_missing_some_data, num_missing_all_data, (num_missing_some_data + num_missing_all_data), skipped_for_credit, med_time]) + '\n')

  with open('CSV/' + book + '_slideshow_rushing_threshold.csv', 'w') as file:
    file.writelines('Bins of Normalized Time Per Slide,Bin size = %s seconds\n' % bin_size)
    file.writelines('Time (Seconds),Number of Slideshows Whose Normalized Time Per Slide is in Each Time Range\n')

    # Keep a count of the number of slideshows encountered, for comparison against quartiles
    count_ss_time = 0

    # Stores the time when each quartile is reached
    quartile_times = [0, 0, 0]

    # Loop through bins
    for bin_num in xrange(max(avg_step_time_bins.keys()) + 1):
      # If the bin has a count, print it, otherwise print 0
      bin_time = (bin_num + 1) * bin_size

      if bin_num in avg_step_time_bins:
        file.writelines('%s,%s\n' % (bin_time, avg_step_time_bins[bin_num]))

        # Increment count by number of modules in bin
        count_ss_time += avg_step_time_bins[bin_num]

        if quartile_times[0] == 0 and count_ss_time > (total_num_ss_times / 4):
          quartile_times[0] = bin_time
        elif quartile_times[1] == 0 and count_ss_time > (total_num_ss_times / 2):
          quartile_times[1] = bin_time
        elif quartile_times[2] == 0 and count_ss_time > (total_num_ss_times * 3 / 4):
          quartile_times[2] = bin_time
      else:
        file.writelines('%s,\n' % bin_time)
    
    file.writelines('\nQuartiles (%s second resolution)\n1st,2nd,3rd\n' % bin_size)
    file.writelines(','.join(str(t) + ' sec' for t in quartile_times))

  with open('CSV/' + book + '_slideshow_median_histogram.csv', 'w') as file:
    file.writelines('Histogram of Median Normalized Time Per Slide,Bin size = %s seconds\n' % median_bin_size)
    file.writelines('Time (Seconds),Number of Students Whose Median Time Per Slide is in Each Time Range\n')

    # Loop through bins
    for bin_num in xrange(max(median_time_bins.keys()) + 1):
      # If the bin has a count, print it, otherwise print 0
      if bin_num in median_time_bins:
        file.writelines('%s,%s\n' % ((bin_num + 1) * median_bin_size, median_time_bins[bin_num]))
      else:
        file.writelines('%s,0\n' % bin_num)

  return render_to_response("developer_view/default_csv_view.html")

@staff_member_required
def cheating_exercises(request, book):
  # Calculate total number of times each proficiency exercise is completed (with respect to the current book)
  # Calculate total number of times students used an AV for assistance on each proficiency exercise

  # Calculate total number of proficiency exercises each user completes
  # Calculate total number of proficiency exercises on which each user used an AV for assistance

  # Maps proficiency exercises to the AV that could be used for assistance (some PE don't have a matching AV and are therefore excluded)
  # 11 (mergesortProficiency) -> 64 (mergesortAV)
  # 16 (ShellsortProficiency) -> 15 (shellsortAV)
  # 47 (quicksortProficiency) -> 46 (quicksortAV)
  pe_av_map = {11: 64, 16: 15, 47: 46}

  # Select all users of a given book, except staff accounts, the phantom (guest) account and abandoned accounts
  users = UserBook.objects.filter(book=book, user__is_staff=0).exclude(user__username='phantom').exclude(user__in=accounts_to_ignore[int(book)]).order_by('id').values_list('user_id', flat=True)
  users = [user for user in users]
  users.sort()

  # Filter events to show only those from proficiency exercises that can be cheated on and their associated AVs
  user_buttons_query = UserButton.objects.filter(book=book, exercise__in=(pe_av_map.keys() + pe_av_map.values()), name__in=['odsa-exercise-init', 'jsav-exercise-reset', 'window-unload', 'jsav-exercise-grade-change']).order_by('action_time').values('name', 'exercise', 'uiid', 'description')

  pe_data = OrderedDict()
  user_data = {}

  # Initialize the structure which holds the total number of times an exercise (that could be cheated on) was attempted, completed or cheated on
  for pe in pe_av_map.keys():
    pe_data[pe] = {'assisted': 0, 'proficient': 0, 'completed': 0, 'attempted': 0}

  # Initialize the structure which holds the total number of proficiency exercises (that could be cheated on) a user attempted, completed or cheated on
  for user in users:
    user_data[user] = {'assisted': 0, 'proficient': 0, 'completed': 0, 'attempted': 0}

    # Show events belonging to a single user
    user_buttons = user_buttons_query.filter(user=user)

    for i in xrange(len(user_buttons)):
      ub = user_buttons[i]
      ub_exer_id = ub['exercise']

      # If the event is the init event of a proficiency exercise, look ahead for a matching AV init event or a suitable end event
      if ub_exer_id in pe_av_map.keys() and ub['name'] == 'odsa-exercise-init':
        # Increment the attempt counters
        pe_data[ub_exer_id]['attempted'] += 1
        user_data[user]['attempted'] += 1

        # Look ahead from current location
        for j in xrange(i, len(user_buttons)):
          ub2 = user_buttons[j]

          # Stop looking if the user finished the proficiency exercise (encountered a reset, window-unload or a 'jsav-exercise-grade-change' event where "complete: 1.0" for the given instance of the proficency exercise)
          if ub2['exercise'] == ub_exer_id and \
             ('uiid' in ub and 'uiid' in ub2 and ub['uiid'] == ub2['uiid']) and \
             (ub2['name'] == 'jsav-exercise-reset' or \
             ub2['name'] == 'window-unload' or \
             (ub2['name'] == 'jsav-exercise-grade-change' and '"complete":1' in ub2['description'])):

            if ub2['name'] == 'jsav-exercise-grade-change':
              pe_data[ub_exer_id]['completed'] += 1
              user_data[user]['completed'] += 1

              # Parse score data from the event description
              score_text = '"score":'
              start_index = ub2['description'].find(score_text) + len(score_text)
              end_index = ub2['description'].find(',', start_index)
              score = float(ub2['description'][start_index:end_index])


              # If score is above the proficiency threshold, increment the proficient count (all PE thresholds are currently 0.9)
              if score >= 0.90:
                pe_data[ub_exer_id]['proficient'] += 1
                user_data[user]['proficient'] += 1

            break

          # Find an init event for the proficiency exercise's matching AV
          elif ub2['exercise'] == pe_av_map[ub_exer_id] and ub2['name'] == 'odsa-exercise-init':

            # Parse the list of array values from the description field of ub
            gen_arr_text = '"gen_array":['
            start_index = ub['description'].find(gen_arr_text) + 4 # Eliminate the '"gen'
            end_index = ub['description'].find(']', start_index) + 1 # Include the trailing ']'

            pe_init_arr = ub['description'][start_index:end_index]
            av_init_text = '"user' + pe_init_arr

            # Search for the list of array values (as a user generated array) in the description of ub2
            if av_init_text in ub2['description']:
              # User 'cheated', increment the user and exercise cheat counts
              user_data[user]['assisted'] += 1
              pe_data[ub_exer_id]['assisted'] += 1

              print 'user: ' + str(user) + ', Match - pe: ' + str(ub_exer_id) + ', uiid: ' + str(ub['uiid']) + ', av: ' + str(ub2['exercise']) + ', uiid: ' + str(ub2['uiid'])

  # Create the CSV directory if necessary
  if not os.path.exists('CSV'):
    os.mkdir('CSV')

  with open('CSV/' + book + '_exercises_cheated_by_student.csv', 'w') as file:
    file.write('User,Assisted,Proficient,Completed,Attempted\n')

    for user in users:
      file.write(','.join(str(x) for x in [user, user_data[user]['assisted'], user_data[user]['proficient'], user_data[user]['completed'], user_data[user]['attempted']]) + '\n')

  with open('CSV/' + book + '_exercises_cheated_by_exercise.csv', 'w') as file:
    file.write('Exercise,Assisted,Proficient,Completed,Attempted\n')

    for pe in pe_data.keys():
      file.write(','.join(str(x) for x in [pe, pe_data[pe]['assisted'], pe_data[pe]['proficient'], pe_data[pe]['completed'], pe_data[pe]['attempted']]) + '\n')

  return render_to_response("developer_view/default_csv_view.html")



















































@staff_member_required
def work_order(request, book):
  # Select all users of a given book, except staff accounts, the phantom (guest) account and abandoned accounts
  users = UserBook.objects.filter(book=book, user__is_staff=0).exclude(user__username='phantom').exclude(user__in=accounts_to_ignore[int(book)]).order_by('id').values_list('user_id', flat=True)
  users = [user for user in users]
  users.sort()

  mod_order = ['SortIntro', 'InsertionSort', 'InsertOpt', 'BubbleSort', 'SelectionSort', 'SortCompare', 'ExchangeSort', 'Shellsort', 'Mergesort', 'MergesortImpl', 'Quicksort', 'Heapsort', 'BinSort', 'RadixSort', 'SortingEmpirical', 'SortingLowerBound', 'SortSumm', 'HashIntro', 'HashFunc', 'HashFuncExamp', 'OpenHash', 'BucketHash', 'HashCSimple', 'HashCImproved', 'HashAnal', 'HashDel', 'HashSumm']

  user_mod_data = OrderedDict()

  # Get UserModule objects
  user_modules = UserModule.objects.filter(book=book, user__in=users).order_by('user').only('user', 'module', 'first_done', 'proficient_date')

  unknown_mods = set()

  for um in user_modules:
    # The first time we encounter a student, initialize their module list with empty tuples
    if um.user.id not in user_mod_data:
      user_mod_data[um.user.id] = [('', '')] * len(mod_order)

    # Find the index of the module to save the time stamps of
    if um.module.name in mod_order:
      mod_index = mod_order.index(um.module.name)
      user_mod_data[um.user.id][mod_index] = (um.first_done, um.proficient_date)
    else:
      unknown_mods.add(um.module.name)

  # Print a list of unknown modules that were encountered (make sure we don't miss any we are interested in)
  if len(unknown_mods) > 0:
    print 'ERROR: Unknown modules'

    for mod in unknown_mods:
      print '  ' + mod

  # Create the CSV directory if necessary
  if not os.path.exists('CSV'):
    os.mkdir('CSV')

  # Write data out to appropriate CSV files
  with open('CSV/' + book + '_mod_order_started.csv', 'w') as started, open('CSV/' + book + '_mod_order_finished.csv', 'w') as finished:
    #started.write('Module Order Started (' + course_name[int(book)] + ')\n')
    #started.write('Module Number,' + ','.join(str(user_id) for user_id in user_mod_data.keys()) + '\n')
    #finished.write('Module Order Completed (' + course_name[int(book)] + ')\n')
    #finished.write('Module Number,' + ','.join(str(user_id) for user_id in user_mod_data.keys()) + '\n')

    # Order modules 1 thru N
    #for i in xrange(1, len(mod_order) + 1):
    #  started.write(str(i) + ',' + ','.join([str(mod_list[i - 1][0]) for id, mod_list in user_mod_data.items() if str(mod_list[i - 1][0]) != '2012-01-01 00:00:00']) + '\n')
    #  finished.write(str(i) + ',' + ','.join([str(mod_list[i - 1][1]) for id, mod_list in user_mod_data.items() if str(mod_list[i - 1][1]) != '2012-01-01 00:00:00']) + '\n')

    started.write('Module Order Started (' + course_name[int(book)] + ')\n')
    started.write('User,' + ','.join(mod_order) + '\n')
    finished.write('Module Order Completed (' + course_name[int(book)] + ')\n')
    finished.write('User,' + ','.join(mod_order) + '\n')

    for id, mod_list in user_mod_data.items():
      # Ignore default dates
      started.write(str(id) + ',' + ','.join([str(start_time) if str(start_time) != '2012-01-01 00:00:00' else '' for start_time, finish_time in mod_list]) + '\n')
      finished.write(str(id) + ',' + ','.join([str(finish_time) if str(finish_time) != '2012-01-01 00:00:00' else '' for start_time, finish_time in mod_list]) + '\n')

  exer_order = ["SortIntroSumm", "InssortCON1", "InssortCON2", "InssortCON3", "insertionsortAV", "InssortPRO", "InssortSumm", "BubsortCON1", "BubsortCON2", "bubblesortAV", "BubsortPRO", "BubsortSumm", "SelsortCON1", "SelsortCON2", "selectionsortAV", "SelsortPRO", "SelsortSumm", "SortCompareSumm", "FindInversionsPRO", "ExchangeSumm", "shellsortCON1", "shellsortCON2", "shellsortCON4", "shellsortCON5", "shellsortCON7", "shellsortCON9", "ShellsortSublist", "shellsortAV", "ShellsortSeries", "ShellsortProficiency", "ShellsortPerformance", "ShellsortSumm", "mergesortAV", "mergesortCON1", "MergesortPRO", "mergesortProficiency", "mergeImplCON1", "mergeImplCON2", "MergesortSumm", "QuicksortPivotPRO", "quicksortAV", "QuicksortCON1", "QuicksortPartitPRO", "quicksortProficiency", "QuicksortSumm", "heapsortCON", "HeapsortPRO", "heapsortProficiency", "HeapsortSumm", "BinsortCON1", "BinsortCON2", "radixLinkAV", "RadixsortPRO", "radixArrayAV", "RadixSortSumm", "SortAlgCompSumm", "SortBoundSumm", "ChapterSumm", "hashIntroCON1", "Birthday", "hashFuncExCON1", "hashFuncExCON2", "MidSquare", "StringSimple", "StringSfold", "HashFuncPROSumm", "HashFuncSumm", "OpenHashPRO", "buckethashCON1", "buckethashCON2", "HashingBucketPRO", "HashingBucket2PRO", "linProbeCON1", "linProbeCON2", "HashingLinearProbePRO", "collisionCON1", "collisionCON2", "HashingLinearStepProbePRO", "collisionCON3", "HashingPseudoRandomProbePRO", "collisionCON4", "collisionCON5", "HashingQuadraticProbePRO", "collisionCON6", "collisionCON7", "collisionCON8", "HashingDoubleProbePRO", "HashAnalSumm", "hashdelCON1", "HashingDeleteProficiency", "HashDelSumm", "HashChapterSumm"]

  # User exercise data
  ued = OrderedDict()

  user_exers = UserExercise.objects.filter(user__in=users).order_by('user')

  unknown_exers = set()

  for ue in user_exers:
      # The first time we encounter a student, initialize their exercise list with empty tuples
      if ue.user.id not in ued:
        ued[ue.user.id] = [('', '')] * len(exer_order)

      # Find the index of the module to save the time stamps of
      if ue.exercise.name in exer_order:
        exer_index = exer_order.index(ue.exercise.name)
        ued[ue.user.id][exer_index] = (ue.first_done, ue.proficient_date)
      else:
        unknown_exers.add(ue.exercise.name)

  # Print a list of unknown exercises that were encountered (make sure we don't miss any we are interested in)
  if len(unknown_exers) > 0:
    print 'ERROR: Unknown exercises'

    for exer in unknown_exers:
      print '  ' + exer

  # Write data out to appropriate CSV files
  with open('CSV/' + book + '_exer_order_started.csv', 'w') as started, open('CSV/' + book + '_exer_order_finished.csv', 'w') as finished:
    started.write('Exercise Order Started (' + course_name[int(book)] + ')\n')
    started.write('User,' + ','.join(exer_order) + '\n')
    finished.write('Exercise Order Completed (' + course_name[int(book)] + ')\n')
    finished.write('User,' + ','.join(exer_order) + '\n')

    for id, exer_list in ued.items():
      # Ignore default dates
      started.write(str(id) + ',' + ','.join([str(start_time) if str(start_time) != '2012-01-01 00:00:00' else '' for start_time, finish_time in exer_list]) + '\n')
      finished.write(str(id) + ',' + ','.join([str(finish_time)  if str(finish_time) != '2012-01-01 00:00:00' else '' for start_time, finish_time in exer_list]) + '\n')

  return render_to_response("developer_view/default_csv_view.html")


@staff_member_required
def non_required_exercise_use(request):
  book = 5

  # Select all users of a given book, except staff accounts, the phantom (guest) account and abandoned accounts
  users = UserBook.objects.filter(book=book, user__is_staff=0).exclude(user__username='phantom').exclude(user__in=accounts_to_ignore[int(book)]).order_by('id').values_list('user_id', flat=True)
  users = [user for user in users]
  users.sort()

  # Get slideshow events
  started_exers = UserButton.objects.filter(book=book, user__in=users, exercise__ex_type='ss', name__in=['jsav-forward', 'jsav-backward', 'jsav-begin', 'jsav-end']).order_by('user').values_list('user_id', 'exercise__name')
  prof_exers = UserExercise.objects.filter(user__in=users, exercise__ex_type='ss', proficient_date__gt=datetime.date(2012,1,1)).order_by('user').values_list('user_id', 'exercise__name')

  # Create an ordered dictionary to start user exercise data, so the order will always be the same when the template iterates through the list (make sure all the columns line up properly)
  ued = OrderedDict()

  for user_id in users:
    ued[user_id] = OrderedDict()
    ued[user_id]['started_exers'] = set()
    ued[user_id]['prof_exers'] = set()

  for user_id, exercise in started_exers:
    ued[user_id]['started_exers'].add(exercise)

  for user_id, exercise in prof_exers:
    ued[user_id]['prof_exers'].add(exercise)

  # Create the CSV directory if necessary
  if not os.path.exists('CSV'):
    os.mkdir('CSV')

  # Write data out to appropriate CSV files
  with open('CSV/non_required_exercise_use.csv', 'w') as file:
    file.write('Non-Required Exercise Use (CS3114A),,Started = Started - Complete (for easy stacked graphs)\n')
    file.write('User,Completed,Started,Missing\n')

    for user_id in users:
      # Calculate the number of exercises that appear in the proficient list but not the started list
      missing_exers = ued[user_id]['prof_exers'] - ued[user_id]['started_exers']

      # Correct the list of started exercises to include the missing ones
      ued[user_id]['started_exers'] = ued[user_id]['started_exers'].union(missing_exers)

      # Add a count of missing exercises to user exercise data object
      ued[user_id]['num_missing'] = len(missing_exers)

      if len(missing_exers) > 0:
        print 'User ' + str(user_id) + ' is missing data from ' + str(len(missing_exers)) + ' exercises'


      id = str(user_id)
      num_prof = str(len(ued[user_id]['prof_exers']))
      num_missing = str(len(missing_exers))

      # Set num_started to be the difference between the number of started exercises and proficient exercises
      # so Excel will create the stacked column graph appropriately
      num_started = str(len(ued[user_id]['started_exers']) - len(ued[user_id]['prof_exers']))

      file.write(','.join([id, num_prof, num_started, num_missing]) + '\n')

  return render_to_response("developer_view/non_req_exercises.html", {'exercises': ued, 'user_exer_data': ued}) #'exercises': ss_order

































# Return a list of unique elements from the given list
def get_unique(list):
  # Eliminate duplicates
  seen = set()
  seen_add = seen.add
  list = [ x for x in list if x not in seen and not seen_add(x)]
  return list

@staff_member_required
def exercise_list(request, student):
  interesting_events = ['jsav-end', 'jsav-forward', 'jsav-array-click', 'odsa-award-credit']
  
  userButtons = UserButton.objects.filter(user=student, name__in=interesting_events).only('exercise', 'module', 'name', 'action_time').order_by('action_time')
  
  user_exercises = dict(UserExercise.objects.filter(user=student).values_list('exercise', 'proficient_date'))
  
  exercises = OrderedDict()
  
  for userButton in userButtons:
    if userButton.exercise.name not in exercises:
      #print userButton.exercise
      exercises[userButton.exercise.name] = {}
      exercises[userButton.exercise.name]['id'] = userButton.exercise.id
      exercises[userButton.exercise.name]['module'] = userButton.module.name
      exercises[userButton.exercise.name]['type'] = userButton.exercise.ex_type
      exercises[userButton.exercise.name]['start_time'] = userButton.action_time
      if userButton.exercise.id in user_exercises:
        exercises[userButton.exercise.name]['proficient_time'] = user_exercises[userButton.exercise.id]
      else:
        exercises[userButton.exercise.name]['proficient_time'] = ''
  
  #print [ u.exercise.name for u in userButtons]
  #print exercises

  return render_to_response("developer_view/exercise_list.html", {'exercises': exercises, 'student': student})

@staff_member_required
def slideshow_cheating(request, student):
  # Maps an exercise name to a dictionary which which stores the number of times a student completed the slideshow (key: 'completed' and the number of times they cheated on the slideshow ('cheated')
  exer_data = OrderedDict()
  
  # List of exercise names where the student cheated to obtain proficiency
  cheated_for_prof_names = []
  
  # Filter UserExerciseLog by user and slideshows where the user gained proficiency
  # Possible to also limit by a time threshold (to reduce the number of results that require processing, but then we can't determine the total number of completions (time_taken__lte=2)
  user_exercise_logs = UserExerciseLog.objects.filter(user=student, exercise__ex_type='ss', earned_proficiency=1).order_by('time_done').only('exercise', 'time_taken', 'count_attempts')
  
  #print user_exercise_logs.query
  #print 'Count: ' + str(user_exercise_logs.count())
  #print user_exercise_logs.values('id', 'time_taken')
  
  # Load a single user's slideshow event data (limited to the exercises and uiids found above)
  ss_events = UserButton.objects.filter(user=student, name__in=['jsav-forward', 'jsav-backward', 'jsav-begin', 'jsav-end']).order_by('action_time')
  
  for uel in user_exercise_logs:
    exer_name = uel.exercise.name
    exer_uiid = uel.count_attempts
    
    # Get the descriptions of events from a specific exercise instance
    descriptions = ss_events.filter(exercise__name=exer_name, uiid=exer_uiid).values_list('description', flat=True)
    print descriptions
    
    # Initialize the completed and cheated counters for the exercise
    if exer_name not in exer_data:
      exer_data[exer_name] = OrderedDict()
      exer_data[exer_name]['cheated'] = 0
      exer_data[exer_name]['completed'] = 0
    
    # Increment the completed counter
    exer_data[exer_name]['completed'] += 1
    
    if len(descriptions) > 0:
      # Parse the total number of slides from the description
      num_slides = descriptions[0].split(' / ')[1]
      
      # Ensure every slide was viewed
      for i in range(1, int(num_slides) + 1):
        if str(i) + ' / ' + num_slides not in descriptions:
          exer_data[exer_name]['cheated'] += 1
          
          # Record whether or not the user cheated the first time they obtained proficiency
          if exer_data[exer_name]['completed'] == 1:
            cheated_for_prof_names.append(exer_name)
          
          print 'CHEAT'
          break
    
    print '\n\n'
  
  return render_to_response("developer_view/slideshow_cheating.html", {'exer_data': exer_data, 'cheated_for_prof': cheated_for_prof_names})

@staff_member_required
def total_module_time(request):
  events = ['document-ready', 'window-unload', 'window-blur', 'window-focus']
  
  user_data = OrderedDict()
  
  modules = []
  
  # Loop through all students
  for ud in UserData.objects.filter(book__in=[5, 6]):
    user_buttons = UserButton.objects.filter(user=ud.user, name__in=events).order_by('action_time')
    
    uid = ud.user.id
    
    user_data[uid] = {}
    
    for i in range(0, len(user_buttons)):
      if user_buttons[i].name == 'document-ready':
        mod_name = user_buttons[i].module.name
        
        if mod_name not in modules:
          modules.append(mod_name)
      
        # Initialize the module time
        if mod_name not in user_data[uid]:
          user_data[uid][mod_name] = 0
        
        last_event_time = user_buttons[i].action_time
        
        # Look ahead for a matching 'window-unload' event, subtracting time when the module doesn't have focus
        for j in range(i, len(user_buttons)):
          if user_buttons[j].module.name == mod_name:
            if user_buttons[j].name in ['window-blur', 'window-unload']:
              # Calculate the difference (in seconds) between the time of this event and the previous one
              user_data[uid][mod_name] += time.mktime(user_buttons[j].action_time.timetuple()) - time.mktime(last_event_time.timetuple())
              
              # Break out of the look-ahead loop when a matching 'window-unload' event has been found
              if user_buttons[j].name == 'window-unload':
                break
            elif user_buttons[j].name == 'window-focus':
              last_event_time = user_buttons[j].action_time
  
  return render_to_response("developer_view/total_module_time.html", {'modules': modules, 'user_data': user_data})

























#exeStat class: exercise, and average proficiency score
class exeStat:
    def __init__(self, exercise, score):
        self.exercise = exercise
        self.score = score

#function to display the statistics of exercises
#return the percentage of people that have achieved proficiency for each exercise
@staff_member_required
def exercises_stat(request):
    userExercise = UserExercise.objects.order_by('exercise').all();
        
    temp = ''   
    proficient =  0.0 #float fro division
    exercises = []
    
    for userExe in userExercise:
        if userExe.exercise == temp:
            if userExe.is_proficient():
                proficient = proficient + 1.0
        else:
            if not temp == '':
                exercises.append(exeStat(temp, round(proficient/60.0, 2)))
            proficient = 0.0
            temp = userExe.exercise;
                
    return render_to_response("developer_view/exercises_stat.html", {'exercises': exercises })

#function to display a graph for the statistics of exercises
#return the total number of proficiency achieved for each exercise
@staff_member_required
def exercises_bargraph(request):
    
    userExercise = UserExercise.objects.order_by('exercise').all();
        
    temp = ''   
    proficient =  0
    exercises = []
    
    for userExe in userExercise:
        if userExe.exercise == temp:
            if userExe.is_proficient():
                proficient = proficient + 1
        else:
            if not temp == '':
                exercises.append(exeStat(temp, proficient))
            proficient = 0
            temp = userExe.exercise;
                
    return render_to_response("developer_view/exercises_bargraph.html", {'exercises': exercises })

#function to display a time distribution graph for the statistics of exercises
#return the average time taken for an exercise
#TODO: debug
@staff_member_required
def exercises_time(request):
    
    userExerciseLog = UserExerciseLog.objects.order_by('exercise').all();
        
    temp = ''   
    time =  0
    exercises = []
    count = 0
    
    for userExeLog in userExerciseLog:
        if userExeLog.exercise == temp:
            time = time + userExeLog.time_taken
            count = count + 1;
        else:
            if not temp == '':
                exercises.append(exeStat(temp, round(time/count, 2)))
            count = 0
            time = 0.0
            temp = userExeLog.exercise;
                
    return render_to_response("developer_view/exercises_time.html", {'exercises': exercises })

@staff_member_required
def student_list_home(request, course_instance = None):


    if course_instance:
        students = []
        course = CourseInstance.objects.get(instance_name = course_instance)
        books = Books.objects.filter(courses = course)
        for book in books:
            bookstudents = UserBook.objects.filter(book = book)
            for profile in bookstudents:
                if not profile.user.is_staff and not profile.user.is_superuser and profile.grade:
                    students.append(profile.user)
        return render_to_response("developer_view/student_list.html", {'students': students, 'course': course_instance })
    else:
        courses_intances = CourseInstance.objects.all()
        context = RequestContext(request,{'open_instances': courses_intances,'STATIC_URL':STATIC_URL})
        return render_to_response("opendsa/student_list_home.html", context)


#This function responds student list (not staff or super user)
#The student information includes id(in the database), user name, and email, etc
@staff_member_required
def student_list(request):

    courses_intances = CourseInstance.objects.all()
    #userProfiles = UserProfile.objects.all();
    students = []
    for course in courses_intances:
        course_students = []
        books = Books.objects.filter(courses=course)
        for book in books:
            bookstudents = UserBook.objects.filter(book=book)
            for profile in bookstudents:
                if not profile.user.is_staff and not profile.user.is_superuser and profile.grade:
                    course_students.append(profile.user) 
    
    for profile in userProfiles:
        if not profile.user.is_staff and not profile.user.is_superuser:
                students.append(profile.user)
    
    return render_to_response("developer_view/student_list.html", {'students': students })

class document_ready_activity:
    def __init__(self, module, activity_num, max):
        
        self.module = module
        self.activity_num = activity_num
        self.max = max
     
    def update_activity(self):
        self.activity_num = self.activity_num + 1
        
    def set_max(self, max):
        self.max = max
        
    def get_activity_num_print(self):
        return float(self.activity_num)/float(self.max)*1000.0
    
class proficient_exercises:
    def __init__(self, date, exercises, number):
        self.date = date
        self.exercises = exercises
        self.number = number
        
    def add_exercise(self,exercise):
        self.exercises.append(exercise)
        self.number = self.number + 1

    def get_number_print(self):
        return self.number*20

@staff_member_required
def student_exercise(request, course, student):
    userButtons = UserButton.objects.filter(user=student, name='document-ready')

    activities = []
    max = 0
    
    for userButton in userButtons:
        flag = 0
        for activity in activities:
            if activity.module == userButton.module:
                activity.update_activity()
                if max < activity.activity_num:
                    max = activity.activity_num
                flag = 1
                break
        if flag == 0:
            doc_activity = document_ready_activity(userButton.module, 1, 0)
            if max < doc_activity.activity_num:
                max = doc_activity.activity_num
            activities.append(doc_activity)
        #else:
         #   if userButton.name == 'jsav-forward' or userButton.name == 'jsav-backward':
         #       doc_activity.update_activity()
    
    #number = len(activities)
    
    for activity in activities:
        activity.set_max(max)
    
    userExercises = UserExercise.objects.filter(user=student).order_by('proficient_date')
    
    exercises = []
    
    for userExercise in userExercises:
        if userExercise.is_proficient():
            flag = 0
            date = userExercise.proficient_date.date()
            for exercise in exercises:
                if date == exercise.date:
                    exercise.add_exercise(userExercise.exercise)
                    flag = 1
                    break
            if flag == 0:
                temp = [userExercise.exercise]
                exercises.append(proficient_exercises(date, temp, 1))
        
    return render_to_response("developer_view/student_exercise.html", {'activities': activities, 'student': student, 'exercises': exercises, 'max': max })

#class of detailed exercise steps
class exercise_step:
    def __init__(self, step_num, time, click_num, is_backward):
        
        self.step_num = step_num
        self.click_num = click_num
        self.time = time
        self.is_backward = is_backward
        
    def set_max_time(self, max_time):
        self.max_time = max_time
        
    def set_max_click(self, max_click):
        self.max_click = max_click
        
    def get_time_print(self):
        return float(self.time)/float(self.max_time)*500.0
    
    def get_click_num_print(self):
        return float(self.click_num)/float(self.max_click)*500.0


@staff_member_required    
def exercise_detail(request, student, exercise):
    #The activities of a user and an exercise
    userButtons = UserButton.objects.filter(user=student).filter(exercise=exercise).order_by('action_time')
    #filter(module=module).
    max_time = 0
    max_click = 0

    exe_steps = []
    current_time = 0
    current_step = 0
    lines = []
    line = []

    #only jsav-forward and jsav-backward actions are handled
    for userButton in userButtons:
        flag = 0

        if userButton.name == 'jsav-forward' and not userButton.description == 'description':
            json_data = json.loads(str(userButton.description))
            step = int(json_data['ev_num'])
            #step = int(userButton.description[:userButton.description.find('/')])

            if current_time == 0 or userButton.action_time < current_time or not step - current_step == 1:
                current_time = userButton.action_time
                current_step = step
                if line:
                    if not len(line) == 1:
                        lines.append(line)
                    line = []
                line.append(current_step)
                continue

            for exe_step in exe_steps:
                if exe_step.step_num == step:
                    exe_step.time = exe_step.time + int((userButton.action_time - current_time).total_seconds())
                    exe_step.click_num = exe_step.click_num + 1
                    flag = 1
                    current_time = userButton.action_time
                    current_step = step
                    line.append(current_step)
                    if max_time < exe_step.time:
                        max_time = exe_step.time
                    if max_click < exe_step.click_num:
                        max_click = exe_step.click_num
                    break
                
            if flag == 0:
                time_diff = int((userButton.action_time - current_time).total_seconds())
                exe_steps.append(exercise_step(step, time_diff, 1, 'false'))
                if max_time < time_diff:
                     max_time = time_diff           
                if max_click < 1:
                    max_click = 1
                current_time = userButton.action_time
                current_step = step
                line.append(current_step)
                
        if userButton.name == 'jsav-backward' and not userButton.description == 'description':
            json_data = json.loads(str(userButton.description))
            step = int(json_data['ev_num'])
            #step = int(userButton.description[:userButton.description.find('/')])

            if current_time == 0 or userButton.action_time < current_time or not step - current_step == -1:
                current_time = userButton.action_time
                current_step = step
                if line:
                    if not len(line) == 1:
                        lines.append(line)
                    line = []
                line.append(current_step)
                continue            
            
            for exe_step in exe_steps:
                if exe_step.step_num == step:
                    exe_step.time = exe_step.time + int((userButton.action_time - current_time).total_seconds())
                    exe_step.click_num = exe_step.click_num + 1
                    if max_time < exe_step.time:
                        max_time = exe_step.time          
                    if max_click < exe_step.click_num:
                        max_click = exe_step.click_num
                    exe_step.is_backward = 'true'
                    flag = 1
                    current_time = userButton.action_time
                    current_step = step
                    line.append(current_step)
                    break
                
            if flag == 0:
                time_diff = int((userButton.action_time - current_time).total_seconds())                
                exe_steps.append(exercise_step(step, time_diff, 1, 'true'))  
                if max_time < time_diff:
                     max_time = time_diff
                     
                if max_click < 1:
                    max_click = 1
                    
                current_time = userButton.action_time
                current_step = step
                line.append(current_step)
                
    if line and not len(line) == 1:
        lines.append(line)
        
    for exe_step in exe_steps:
        exe_step.set_max_time(max_time)
        exe_step.set_max_click(max_click)
    #number = len(exe_steps)
    
    exe_steps = sorted(exe_steps, key=lambda exercise_step:exercise_step.step_num)
                  
    #print(max)
    
    userExercises = UserExercise.objects.filter(user=student).filter(exercise=exercise)
    
    review_dates = []
    
    if len(userExercises) == 1 and userExercises[0].is_proficient():
        
        proficient_date = userExercises[0].proficient_date
        
        exercise = userExercises[0].exercise
    
        userButtons = UserButton.objects.filter(action_time__gt = proficient_date).filter(user=student).filter(exercise=exercise)
        
        #print(userButtons)
        
        for userButton in userButtons:
            if proficient_date.date() < userButton.action_time.date():
                #print(userButton.user_id)
                review_dates.append(userButton.action_time.date())
                
        proficient_date = proficient_date.date()
        
    else:
        proficient_date = 'not_proficient'
        exercise = ''
    
    review_dates = list(set(review_dates))
    
    #print(proficificent_date)
    
    return render_to_response("developer_view/exercise_detail.html", {'exe_steps': exe_steps, 'proficient_date': proficient_date, 'review_dates':review_dates, 'lines': lines, 'exercise':exercise })

#The class to keep document ready event
class docready_event():
    def __init__(self, year, month, day, module):
        self.year = year
        self.month = month
        self.day = day
        self.module = module
        
    def equals(self, year, month, day, module):
        if self.year == year and self.month == month and self.day == day and self.module == module:
            return 1;
        return 0;

#The first time line model
@staff_member_required
def timeline_sum(request, student):
    #This query fetches the document ready activities of a user
    userButtons = UserButton.objects.filter(user=student).filter(name='document-ready')
    
    events = []

    for userButton in userButtons:
        flag = 0
        for event in events:
            if event.equals(userButton.action_time.year, userButton.action_time.month, userButton.action_time.day, userButton.module) == 1:
                flag = 1
                break
        
        if flag == 0:
            events.append(docready_event(userButton.action_time.year, userButton.action_time.month, userButton.action_time.day, userButton.module))

    #events = list(set(events))
    for event in events:
        print(event.month)

    return render_to_response("developer_view/timeline_sum.html", {'events': events, 'student':student})

#the event class to keep for the timeline detail view
class general_event():
    def __init__(self, year, month, day, hour, minute, second, exercise, description):
        self.year = year
        self.month = month
        self.day = day
        self.hour = hour
        self.minute = minute
        self.second = second
        self.exercise = exercise
        self.description = description
        

#time line detail model
@staff_member_required
def timeline_detail(request, student, module, year, month, day):
    
    #This query fetches the activities of a user, a model, an action date except the document ready actions
    userButtons = UserButton.objects.filter(user=student).filter(module__name=module).filter(action_time__year=year).filter(action_time__month=month).filter(action_time__day=day).exclude(name='document-ready')

    events = []

    for userButton in userButtons:
        events.append(general_event(userButton.action_time.year, userButton.action_time.month, userButton.action_time.day, userButton.action_time.hour, userButton.action_time.minute, userButton.action_time.second, userButton.exercise, userButton.description))

    return render_to_response("developer_view/timeline_detail.html", {'events':events})
