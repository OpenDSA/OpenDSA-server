import re
import os
import itertools
import hashlib
import urllib
import logging


import datetime
import models
import simplejson as json

from opendsa.models import Exercise, UserExercise, UserExerciseLog, UserData
from django.conf.urls.defaults import patterns, url
from django.contrib.auth import authenticate, login
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.utils import simplejson
from django.contrib.sessions.models import Session



def str2bool(v):
  return v.lower() in ("yes", "true", "t", "1")


def make_wrong_attempt(user_data, user_exercise):
    if user_exercise and user_exercise.belongs_to(user_data):
        user_exercise.update_proficiency_model(correct=False)
        user_exercise.put()

        return user_exercise

def attempt_problem(user_data, user_exercise, attempt_number,
    completed, count_hints, time_taken,
    ip_address):

    if user_exercise:   # and user_exercise.belongs_to(user_data):
        print user_exercise  
        dt_now = datetime.datetime.now()
        exercise = user_exercise.exercise 
        user_exercise.last_done = dt_now
        # Build up problem log for deferred put
        problem_log = models.UserExerciseLog(
                user=user_data, 
                exercise=user_exercise.exercise,
                time_taken=time_taken,
                time_done=dt_now,
                count_hints=count_hints,
                hint_used=int(count_hints) > 0,
                correct=completed and not str2bool(count_hints) and (int(attempt_number) == 1),
                count_attempts=attempt_number,
                ip_address=ip_address,
        )


        first_response = (attempt_number == 1 and count_hints == 0) or (count_hints == 1 and attempt_number == 0)

        if user_exercise.total_done > 0 and user_exercise.streak == 0 and first_response:
            bingo('hints_keep_going_after_wrong')

        just_earned_proficiency = False

        # Users can only attempt problems for themselves, so the experiment
        # bucket always corresponds to the one for this current user
        #struggling_model = StrugglingExperiment.get_alternative_for_user(
        #         user_data, current_user=True) or StrugglingExperiment.DEFAULT
        if completed:

            user_exercise.total_done += 1

            if problem_log.correct:

                proficient = user_data.is_proficient_at(user_exercise.exercise)

                #explicitly_proficient = user_data.is_explicitly_proficient_at(user_exercise[0].exercise)
                #suggested = user_data.is_suggested(user_exercise[0].exercise)
                #problem_log.suggested = suggested

                problem_log.points_earned = 4  #points.ExercisePointCalculator(user_exercise[0], suggested, proficient)
                #user_data.add_points(problem_log.points_earned)

                # Streak only increments if problem was solved correctly (on first attempt)
                user_exercise.total_correct += 1
                user_exercise.streak += 1
                user_exercise.longest_streak = max(user_exercise.longest_streak, user_exercise.streak)

                if not proficient: 
                    if exercise.ex_type == 'ka':
                        problem_log.earned_proficiency = user_exercise.update_proficiency_ka(correct=True)
                    
   
#                bingo('struggling_problems_correct')

#                if user_exercise[0].progress >= 1.0 and not explicitly_proficient:
#                    bingo(['hints_gained_proficiency_all',
#                           'struggling_gained_proficiency_all',
#                           'homepage_restructure_gained_proficiency_all'])
#                    if not user_exercise[0].has_been_proficient():
#                        bingo('hints_gained_new_proficiency')

#                    if user_exercise.history_indicates_struggling(struggling_model):
#                        bingo('struggling_gained_proficiency_post_struggling')

#                    user_exercise[0].set_proficient(user_data)
#                    user_data.reassess_if_necessary()

#                    just_earned_proficiency = True
#                    problem_log.earned_proficiency = True

#            util_badges.update_with_user_exercise(
#                user_data,
#                user_exercise,
#                include_other_badges=True,
#                action_cache=last_action_cache.LastActionCache.get_cache_and_push_problem_log(user_data, problem_log))

            # Update phantom user notifications
#            util_notify.update(user_data, user_exercise)

#            bingo([
#                'hints_problems_done',
#                'struggling_problems_done',
#                'homepage_restructure_problems_done',
#            ])

        else:
            # Only count wrong answer at most once per problem
            if first_response:
                user_exercise.update_proficiency_model(correct=False)
                bingo(['hints_wrong_problems', 'struggling_problems_wrong'])

#            if user_exercisei[0].is_struggling(struggling_model):
#                bingo('struggling_struggled_binary')

        # If this is the first attempt, update review schedule appropriately
#        if attempt_number == 1:
#            user_exercise[0].schedule_review(completed)

#        user_exercise_graph = models.UserExerciseGraph.get_and_update(user_data, user_exercise)

#        goals_updated = GoalList.update_goals(user_data,
#            lambda goal: goal.just_did_exercise(user_data, user_exercise,
#                just_earned_proficiency))

        # Bulk put
#        db.put([user_data, user_exercise, user_exercise_graph.cache])

        # Defer the put of ProblemLog for now, as we think it might be causing hot tablets
        # and want to shift it off to an automatically-retrying task queue.
        # http://ikaisays.com/2011/01/25/app-engine-datastore-tip-monotonically-increasing-values-are-bad/
#        deferred.defer(models.commit_problem_log, problem_log,
#                       _queue="problem-log-queue",
#                       _url="/_ah/queue/deferred_problemlog")

#        if user_data is not None and user_data.coaches:
#            # Making a separate queue for the log summaries so we can clearly see how much they are getting used
#            deferred.defer(models.commit_log_summary_coaches, problem_log, user_data.coaches,
#                       _queue="log-summary-queue",
#                       _url="/_ah/queue/deferred_log_summary")
        problem_log.save()
        return user_exercise.save(),True      #, user_exercise_graph, goals_updated
        
