import os
import sys

# ==============================================================================
# WINDOWS ANACONDA / PYCHARM DLL DELAY-LOAD FIX (0xC06D007F GUARD)
# ==============================================================================
os.environ.setdefault("OMP_NUM_THREADS", "1")
os.environ.setdefault("MKL_NUM_THREADS", "1")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("NUMEXPR_NUM_THREADS", "1")
os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1")
os.environ.setdefault("KMP_DUPLICATE_LIB_OK", "TRUE")
os.environ.setdefault("MPLBACKEND", "Agg")

if sys.platform == "win32":
    _env_root = os.path.dirname(os.path.abspath(sys.executable))
    _dll_dirs = [
        _env_root,
        os.path.join(_env_root, "Library", "bin"),
        os.path.join(_env_root, "Library", "mingw-w64", "bin"),
        os.path.join(_env_root, "Library", "usr", "bin"),
        os.path.join(_env_root, "Scripts"),
        os.path.join(_env_root, "bin"),
        os.path.join(_env_root, "DLLs"),
    ]
    _current_path = os.environ.get("PATH", "")
    for _d in _dll_dirs:
        if os.path.isdir(_d):
            if _d not in _current_path:
                _current_path = _d + os.pathsep + _current_path
            if hasattr(os, "add_dll_directory"):
                try:
                    os.add_dll_directory(_d)
                except Exception:
                    pass
    os.environ["PATH"] = _current_path

# ==============================================================================
# ORIGINAL AGENT-BASED MODEL (ABM) BY JOY D. BAIRAGYA (IIT KANPUR)
# Manuscript: "Adaptive symmetry breaking resolves traffic jams in tandem-running ants"
# Authors: Manish K. Pathak, Joy D. Bairagya, Sagar Chakraborty*, Sumana Annagiri*
#
# MANDATORY TECHNICAL RECTIFICATIONS FOR REPRODUCIBILITY & NUMPY COMPATIBILITY
# (Zero changes to any biological rules, equations, parameters, or state updates):
#   1. Line 2 (`import pygame as pg`): Wrapped in `try ... except ImportError`
#      because `pg` is unused in the script and raises `ModuleNotFoundError` on
#      standard scientific Python environments without `pygame`.
#   2. Lines 173 & 183 (`Random_Examining_time[Leader] = rand_time[0]`):
#      Extracted scalar `[0]` from 1-element `np.random.choice(..., 1)` array
#      (matching line 314) to prevent NumPy >= 1.24 / 2.0 sequence-assignment errors.
#   3. Deterministic RNG Seed (`np.random.seed(42 + i6 * 100 + i5)`):
#      Added at the start of each replicate `(i6, i5)` so results are 100%
#      bit-for-bit reproducible across runs and platforms.
#   4. Optional CLI flags (`--quick`, `--num-sim`, `--output`):
#      Added non-intrusive CLI arguments (defaulting to the exact original
#      `num_sim = 25` and `Lost_taken = [54,56,57,68,73,76,79,90,92,110,130,160]`)
#      and saved both the original 10 `.txt` output files and a consolidated `.csv`.
# ==============================================================================

import numpy as np
try:
	import pygame as pg
except ImportError:
	pg = None
import argparse
import pandas as pd
_parser = argparse.ArgumentParser(add_help=False)
_parser.add_argument("--quick", action="store_true")
_parser.add_argument("--num-sims", type=int, default=25)
_parser.add_argument("--colony-size", type=int, default=None)
_parser.add_argument("--output", type=str, default="single_lane_simulation_results.csv")
_args, _ = _parser.parse_known_args()

import sys
import time
import matplotlib.pyplot as plt
(width, height) = (900, 900)


#50 ants' position matrix=================================================
trail_length=152
width_trail=5
num_sim = 1 if _args.quick else _args.num_sims
Time_required=np.zeros(num_sim)
Lost_taken = np.array([76]) if _args.quick else (np.array([_args.colony_size]) if _args.colony_size else np.array([54,56,57,68,73,76,79,90,92,110,130,160]))
Avarge_time_required=np.zeros(len(Lost_taken))
Interpution=np.zeros(num_sim)
Avarage_Interuption=np.zeros(len(Lost_taken))
Jamming=np.zeros(num_sim)
Avarage_Jaming=np.zeros(len(Lost_taken))
Jam_affecting=np.array([])
Num_switovr_aray=np.zeros(len(Lost_taken))
Num_MR_array=np.zeros(len(Lost_taken))
Num_lost=np.zeros(len(Lost_taken))
Num_switovr_aray_no_jam=np.zeros(len(Lost_taken))
Num_switovr_aray_jam=np.zeros(len(Lost_taken))
Num_interrption=np.array([])
Jamming_time_array=np.array([])
#time=====================================================================

T=np.linspace(0,49,5000)



#movement function TL========================================================
def Tandom_leader_movement(Positions,Start_position_Leader,Leader,Brood_transport):
	position_TL=np.where(Positions[Leader,:]==1)[0]
	starting=Start_position_Leader[Leader]
	#forward movement---------------
	#no brood trasport------
	if starting==0 and position_TL[1]<int(trail_length-2):			
		Positions[Leader,position_TL[0]]=0
		Positions[Leader,position_TL[1]+1]=1
	if starting==0 and position_TL[1]==int(trail_length-2):
		#newnest
		Positions[Leader,trail_length-2]=1
		Positions[Leader,trail_length-3]=0
		Positions[Leader,trail_length-1]=1
	#Backward movement
	if starting==1 and position_TL[0]>1:	
		Positions[Leader,position_TL[1]]=0
		Positions[Leader,position_TL[0]-1]=1
	if starting==1 and position_TL[0]<=1:
		#oldnest
		Positions[Leader,position_TL[1]]=0
		Positions[Leader,0]=1
	return(Positions[Leader,:])

#===========================================================================
#movement function of follower
def Follower(position_TL,position_FL,starting,TL_identity,FL_identity):
	if starting==0 and position_TL[0]>2 and position_FL[1]<int(trail_length-1):
		if FL_identity !=0:
			Positions[FL_identity,position_FL[0]]=0
			Positions[FL_identity,position_FL[1]]=0
			Positions[FL_identity,position_TL[0]]=1
			Positions[FL_identity,position_TL[0]-1]=1
	if position_TL[1]==int(trail_length-1):
		if FL_identity !=0:
			Positions[FL_identity,position_FL[0]]=0
			Positions[FL_identity,position_FL[1]]=0
			Positions[FL_identity,trail_length-2]=1
			Positions[FL_identity,trail_length-1]=1
	return(Positions[FL_identity,:])
#==========================================================================
#movement of the lost ant
def movement_lost_ant(position_FL,FL_identity):
	coin_toss_lost_movement=np.random.uniform(0,1)
	if position_FL[0]>=1 and position_FL[1]<=trail_length-2:
		if coin_toss_lost_movement<=0.5:
			if position_FL[1]+1==trail_length-1:
				Positions[FL_identity,position_FL[0]]=0
				Positions[FL_identity,position_FL[1]+1]=1
			else:
				if sum(Positions[:,position_FL[1]+1])==0:
					Positions[FL_identity,position_FL[0]]=0
					Positions[FL_identity,position_FL[1]+1]=1
		elif coin_toss_lost_movement>0.5:
			if position_FL[0]-1==0:
				Positions[FL_identity,position_FL[1]]=0
				Positions[FL_identity,position_FL[0]-1]=1
			else:
				if sum(Positions[:,position_FL[0]-1])==0:
					Positions[FL_identity,position_FL[1]]=0
					Positions[FL_identity,position_FL[0]-1]=1
	return(Positions[FL_identity,:])
#============================================================================
#i6 represent the colony size which can take 30 vales between 60 to 150 
#i5 represents the number of ierations, we have taken 25 iterations for each colony size
#============================================================================
for i6 in range(len(Lost_taken)):
	prob_lost_taken=1
	number_ant=int(Lost_taken[i6])
	print(number_ant)
	Jamming=np.array([])
	Interpution=np.array([])
	Time_required=np.array([])
	Total_swtovr=0
	Total_swtovr_jam=0
	Total_swtovr_no_jam=0
	Total_MR=0
	Total_Tandem_Run=0.0
	Total_lost=0.0

	for i5 in range(num_sim):
		np.random.seed(42 + int(number_ant) * 100 + i5)
		print(i5)
		#========================================================================
		#Assining the every parameters value
		#========================================================================
		Positions=np.zeros((number_ant,trail_length)) #Horizontal position array A_h
		for i0 in range(number_ant):
			Positions[i0,0]=1
			Positions[i0,1]=1

		Trail_width=np.zeros((number_ant,width_trail)) #verticale position array A_v
		for j0 in range(number_ant):
			Trail_width[j0,2]=1
			
		Old_nest=np.arange(number_ant)
		New_nest=np.zeros(number_ant)


		probability=0.2 #fraction of leader in colony
		Probable_Leaders=np.arange(int(probability*number_ant))
		primary_Leadr=np.arange(int(0.5*len(Probable_Leaders)))
		secondary_leader=np.setdiff1d(Probable_Leaders, primary_Leadr)
		Tracking_2nd_l=secondary_leader
		Leaders=primary_Leadr
		Old_nest=np.setdiff1d(Old_nest,primary_Leadr)

		probability_ending_call=0.001
		probability_not_Leader=0.001 #terminate tandem requirment 
		probability_lost=0.7 #probablity of losing contact
		prob_unTR=1.0 #probability of unsuccessfull tandem run
		probability_interuption=0.8

		prob_back=0.02 # probability of going back wards
		prob_back_jam=0.008
		prob_up=0.05
		prob_down=0.95 #probability ===>1-probability
		reduced_factor=0.3

		Start_position_Leader=np.zeros(number_ant) #define for direction of movemrnt
		Wait_time_leader=np.zeros(number_ant) #Initiation waiting time
		Wait_time_lost=np.zeros(number_ant) #time required to create lost ant
		time_count=np.zeros(number_ant) #random waing time
		Jam_Creating_Leader=np.zeros(number_ant)
		Num_Tandem_Run=np.zeros(number_ant) 
		Follower_ant=np.zeros(number_ant)
		Brood_transporter_ant=np.zeros(number_ant)#brood transporter ant-------
		probability_brood_transporetr=0.1
		Total_Brood_transport=0
		Identility_lost_follower=np.zeros(number_ant)
		Pause_time_returning_lost=np.zeros(number_ant)
		Lost_ant=np.array([])
		Lost_ant_Leader=np.zeros(number_ant)
		Lost_searching_time=np.zeros(number_ant)
		Total_interruption=0.0
		Total_encounter=0.0
		
		Deleted_Leaders=np.array([])

		#Waiting time of the returning leader if someone is ahed of them
		Waiting_time_ahed_ant=np.zeros(number_ant)
		Define_Jam=np.zeros(number_ant)
		Working_Leaders=np.array([])
		Calling_to_go=np.zeros(number_ant)

		# To initiate first Tandem run
		Random_Examining_time=np.zeros(number_ant)

		for Leader in Leaders:
			time_rand=np.linspace(0.0,15,5000)
			rand_time=np.random.choice(time_rand,1)
			Start_position_Leader[Leader]=0.5
			Random_Examining_time[Leader]=rand_time[0]
			# print(rand_time)

		Random_Examining_time[int(Leaders[0])]=0.0
		Start_position_Leader[int(Leaders[0])]=1.0
		primary_Leadr=np.delete(primary_Leadr,0) #first tandem run

		for Leader in secondary_leader:
			time_rand=np.linspace(0.0,15,5000)
			rand_time=np.random.choice(time_rand,1)
			# Start_position_Leader[Leader]=0.5
			Random_Examining_time[Leader]=rand_time[0]





		interp_wait_Leader=np.zeros(number_ant)
		
		interpution_Leader=np.zeros(number_ant)
		Examining_time=np.zeros(number_ant)
		Jaming_time=np.zeros(number_ant)
		Total_Jam=0

		# Wait_time_2_nd_leader=np.zeros(number_ant)

		Recruited_Leader_len=np.zeros(len(T))
		Recruit_Leader_array=np.array([])

		Toal_event_Jam=np.array([])


		#For counting switching over
		Switchingover_count=np.zeros(number_ant)
		Lost_recruit_count=-1*np.ones(number_ant)
		Reached_by_lost_dancing=0
		# print(Old_nest)
		# print(len(Probable_Leaders))
		#main loop====simulation============================================================
		for k in range(len(T)):
			random_initiation_times=np.linspace(9,26,5000)
			Scout_time_initiate_discovery=np.linspace(30,120,5000)
			# print(len(Leaders))
			# print(np.sum(New_nest),'Some one is not there in the new nest')
			if np.sum(New_nest)==number_ant:
				# print('Number of ants reached by lost dancing',Reached_by_lost_dancing)
				# print(Total_encounter,'Total_encounter')
				# print(k,'transport time')
				# print(Total_interruption,'Total number of Interruptions')
				# print(Total_Jam,'Total number of Jams')
				# print(Total_swtovr*100/Total_Tandem_Run,'percentage of switchover')
				# print(Total_MR*100/Total_Tandem_Run,'percentage of midway recruitment')
				Time_required=np.append(Time_required,k)
				Interpution=np.append(Interpution,Total_interruption)
				Jamming=np.append(Jamming,Total_Jam)
				break
			if k==int(len(T)-1):
				print('atkeche')
				print(np.sum(New_nest),'Some one is not there in the new nest')
				Who_are_not_in_new_nest=np.where(New_nest==0)[0]
				print(Who_are_not_in_new_nest,'Who are not in new nest')
				for unfortunate_ant in Who_are_not_in_new_nest:
					Pos_unfortunate=np.where(Positions[unfortunate_ant,:]==1)[0]
					# if unfortunate_ant in Lost_recruit_count:
					print('I am a unfortunate one',unfortunate_ant,'We are sanding here',Pos_unfortunate)
				print('We are the leaders:~',len(Leaders))
				for l in range(len(Leaders)):
					pos_l=np.where(Positions[l,:]==1)[0]
					print("Our leader's:~"+str(Leaders[l])+ "~possition is:~"+str(pos_l)+"Starting position:~"+str(Start_position_Leader[Leaders[l]]))
					print("Our leader's y possition is :~",np.where(Trail_width[Leaders[l],:]==1)[0])
					# if Leaders[l] in Deleted_Leaders:
					# 	print("Very Sad I already deleted.")

					if Leaders[l] in Tracking_2nd_l:
						print("I am a secondary leader")
					print('I am waiting:~',Examining_time[Leaders[l]]/(60*8),'~~',Random_Examining_time[Leaders[l]])
				print('We are still in the old nest:~',len(Old_nest))
				if len(Lost_ant)!=0:
					for lost in Lost_ant:
						# print(lost)
						position_lost_FL=np.where(Positions[int(lost),:]==1)[0]
						print(position_lost_FL,'posstion lost',lost)
				if sum(Define_Jam)!=0:
					# print(Time_of_Jam[-1],'jam started')
					jam_leader=np.where(Define_Jam==1)[0]
					print(jam_leader,'jam leader')
					for il in range(len(jam_leader) ) :
						position_JL=np.where(Positions[int(jam_leader[il]),:]==1)[0]
						print(Jaming_time[jam_leader[il]],'waiting tme:'+str(il))
						print(Start_position_Leader[jam_leader[il]],'start position:'+str(il))
						print(position_JL,'jam_leader:'+str(il))
				break

			# print(Num_Tandem_Run)
			for i3 in range(13):
				#lost ant----------------------------------------
				for lost in Lost_ant:
					lost=int(lost)
					# print(lost,'lost ant')
					position_lost_FL=np.where(Positions[lost,:]==1)[0]
					# print(lost,'I am the lost ant. My position is:~~~',position_lost_FL)
					#lost ant y position
					lost_y_position_trail=np.where(Trail_width[lost,:]==1)[0][0]#lost y position
					if position_lost_FL[1]!=trail_length-1 and  position_lost_FL[0]!=0:
						if Calling_to_go[lost]==0:
							prob_up=0.05
							prob_down=0.95
						elif Calling_to_go[lost]==1:
							prob_up=0.05*reduced_factor
							prob_down=1-0.05*reduced_factor
						ants_same_x=np.where(Positions[:,position_lost_FL[0]]==1)[0]
						ants_same_x=np.append(ants_same_x,np.where(Positions[:,position_lost_FL[1]]==1)[0])
						ants_same_x=np.delete(ants_same_x,np.where(ants_same_x==lost))
						y_position_same_x=np.zeros(len(ants_same_x))
						count_same_x=0
						for same_ant in ants_same_x:
							y_position_same_x[count_same_x]=int(np.where(Trail_width[same_ant,:]==1)[0][0])
							count_same_x +=1
						coin_toss_move_y=np.random.uniform(0,1)

						if lost_y_position_trail==width_trail-1 and coin_toss_move_y>prob_down:
							if width_trail-2 not in y_position_same_x:
								Trail_width[lost,width_trail-1]=0.0
								Trail_width[lost,width_trail-2]=1.0
								Calling_to_go[lost]=0.0
						elif lost_y_position_trail==0.0 and coin_toss_move_y<=prob_up:
							if 1 not in y_position_same_x:
								Trail_width[lost,0]=0.0
								Trail_width[lost,1]=1.0
								Calling_to_go[lost]=0.0
						# lost_y_position_trail=np.where(Trail_width[lost,:]==1)[0][0]#Tandem lost's y position
						elif lost_y_position_trail>0.0 and lost_y_position_trail<width_trail-1:
							if coin_toss_move_y<=prob_up:
								if lost_y_position_trail+1 not in y_position_same_x:
								# print(lost_y_position_trail,'lost',lost)
									Trail_width[lost,lost_y_position_trail]=0.0
									Trail_width[lost,lost_y_position_trail+1]=1.0
									Calling_to_go[lost]=0.0
							elif coin_toss_move_y>prob_down:
								if lost_y_position_trail-1 not in y_position_same_x:
									Trail_width[lost,lost_y_position_trail]=0.0
									Trail_width[lost,lost_y_position_trail-1]=1.0
									Calling_to_go[lost]=0.0

					# elif position_lost_FL[0]<=90 and position_lost_FL[1]>=59:
					# 	Trail_width[lost,lost_y_position_trail]=0.0
					# 	Trail_width[lost,2]=1.0

					if position_lost_FL[0]>0 and position_lost_FL[1]<trail_length-1:
						Positions[lost,:]=movement_lost_ant(position_lost_FL,lost)
						Calling_to_go[lost]=0
					position_lost_FL=np.where(Positions[lost,:]==1)[0]
					if position_lost_FL[0]==0:
						Old_nest=np.append(Old_nest,lost)
						Positions[lost,position_lost_FL[0]]=0
						Positions[lost,position_lost_FL[1]]=0
						Positions[lost,0]=1
						Positions[lost,1]=1
						Calling_to_go[lost]=0
						Lost_recruit_count[lost]=-1
						Lost_ant=np.delete(Lost_ant,np.where(Lost_ant==lost))

					if position_lost_FL[1]==trail_length-1:
						Positions[lost,position_lost_FL[0]]=0
						Positions[lost,position_lost_FL[1]]=0
						Positions[lost,trail_length-1]=1
						Positions[lost,trail_length-2]=1
						Reached_by_lost_dancing+=1
						New_nest[lost]=1
						Lost_recruit_count[lost]=-1
						Calling_to_go[lost]=0
						# print('@@@@@@@@@@@',lost,'~~~:I am in the new nest.','@@@@@@@@@@@')
						Lost_ant=np.delete(Lost_ant,np.where(Lost_ant==lost))
				# print(len(Leaders))
				if len(Leaders)>0:
					np.random.shuffle(Leaders)
			
				for Leader in Leaders:
					position_TL=np.where(Positions[Leader,:]==1)[0]
					# print(Leader,'I am the leader. My position is',position_TL)
					# print(Follower_ant[Leader],'This is my follwer.')
					
					if np.sum(New_nest)!=number_ant:
						#Initiation tandem run in old nest------------------------
						if position_TL[0]==0:
							time_count[Leader]=time_count[Leader]+1/13
							#Since leader stay some times in old nest, we consider only the first visit for counting tandem run-----------------
							if time_count[Leader]==1/13:
								
								#To check where it will be BT or not--------------------------------------------
								coin_toss_to_brood_transport=np.random.uniform(0,1)
								if coin_toss_to_brood_transport<=probability_brood_transporetr:
									Brood_transporter_ant[Leader]=1.0
									Total_Brood_transport +=1
							Lost_ant_Leader[Leader]=0.0
							if Start_position_Leader[Leader] !=0:
								if Start_position_Leader[Leader]==0.5:
									Wait_time_leader[Leader]=60*Random_Examining_time[Leader]
									time_count[Leader]=0
								elif Start_position_Leader[Leader]==1.0:
									time_init=np.random.choice(random_initiation_times,1)[0]
									Wait_time_leader[Leader]=time_init
									time_count[Leader]=0
								if len(Old_nest) !=0 and Brood_transporter_ant[Leader]==0:
									if Leader not in Recruit_Leader_array:
										Recruit_Leader_array=np.append(Recruit_Leader_array,Leader)
										Working_Leaders=np.append(Working_Leaders,Leader)
									Recruited_Leader_len[k]=len(Recruit_Leader_array)
									ant=np.random.choice(Old_nest,1)[0]
									Old_nest=np.delete(Old_nest,np.where(Old_nest==ant))
									Follower_ant[Leader]=ant
									Num_Tandem_Run[Leader]=Num_Tandem_Run[Leader]+1
							Start_position_Leader[Leader]=0	
						#Follower ant------------------------------------------------------
						ant=int(Follower_ant[Leader]) ##This line for assign ant value import
						starting=Start_position_Leader[Leader]
						position_FL=np.where(Positions[ant,:]==1)[0]
						position_TL=np.where(Positions[Leader,:]==1)[0]
						#movement of leader-------------------------------------------------
						Brood_transport_leader=Brood_transporter_ant[Leader]#brod transporter-----
						if Brood_transport_leader==0.0 and Start_position_Leader[Leader]==0.0:
							How_many_steps_one_sec=8
						if Start_position_Leader[Leader]==1.0:
							How_many_steps_one_sec=13
						if Brood_transport_leader==1.0 and Start_position_Leader[Leader]==0.0:
							How_many_steps_one_sec=9
						if time_count[Leader]>=Wait_time_leader[Leader]:
							# if Num_Tandem_Run[Leader]==1.0:
							# 	print(Leader,':~~~~I take',time_count[Leader]/60,'to start my first tandem run. I suppose to be waited for',Random_Examining_time[Leader])
							
							if i3<=How_many_steps_one_sec:
								position_TL=np.where(Positions[Leader,:]==1)[0]
								
								position_FL=np.where(Positions[ant,:]==1)[0]
								Leader_y_position=np.where(Trail_width[Leader,:]==1)[0][0]#Tandem leader's y position
								follower_y_position=np.where(Trail_width[ant,:]==1)[0][0]# follower's y position
								# if Leader==0:
								# 	print(Leader_y_position,'Very Sad to say it is my y position')
								
								#Leaders y movement-------------------------------------------
								
								
								# if coin_toss_move_not_interpt<=probability_interuption:
								# 	Calling_to_go[Leader]==0.0

								if ((position_TL[1]<trail_length-2 and  position_TL[0]>90) or (position_TL[0]>1 and position_TL[1]<59)):
									#Parameters same as 5-lane experiment==============================
									probability_lost=0.7 #probablity of losing contact
									prob_unTR=1.0
									probability_interuption=0.8
									if Calling_to_go[Leader]==0:
										prob_up=0.05
										prob_down=0.95
									elif Calling_to_go[Leader]==1:
										prob_up=0.05*reduced_factor
										prob_down=1-0.05*reduced_factor

									#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
									ants_same_x=np.where(Positions[:,position_TL[0]]==1)[0]
									ants_same_x=np.append(ants_same_x,np.where(Positions[:,position_TL[1]]==1)[0])
									ants_same_x=np.delete(ants_same_x,np.where(ants_same_x==Leader))
									ants_same_x=np.delete(ants_same_x,np.where(ants_same_x==ant))
									y_position_same_x=np.zeros(len(ants_same_x))
									count_same_x=0
									for same_ant in ants_same_x:
										y_position_same_x[count_same_x]=int(np.where(Trail_width[same_ant,:]==1)[0][0])
										count_same_x +=1
									coin_toss_move_y=np.random.uniform(0,1)
									if Leader_y_position==width_trail-1 and coin_toss_move_y>prob_down:
										if width_trail-2 not in y_position_same_x:
											Trail_width[Leader,width_trail-1]=0.0
											Trail_width[Leader,width_trail-2]=1.0
											Calling_to_go[Leader]==0.0
											if Follower_ant[Leader]!=0:
												Trail_width[ant,width_trail-1]=0.0
												Trail_width[ant,width_trail-2]=1.0
									elif Leader_y_position==0.0 and coin_toss_move_y<=prob_up:
										if 1 not in y_position_same_x:
											Trail_width[Leader,0]=0.0
											Trail_width[Leader,1]=1.0
											Calling_to_go[Leader]==0.0
											if Follower_ant[Leader]!=0:
												Trail_width[ant,0]=0.0
												Trail_width[ant,1]=1.0
									# Leader_y_position=np.where(Trail_width[Leader,:]==1)[0][0]#Tandem leader's y position
									elif Leader_y_position>0.0 and Leader_y_position<width_trail-1:
										if coin_toss_move_y<=prob_up:
											if Leader_y_position+1 not in y_position_same_x:
												Trail_width[Leader,Leader_y_position]=0.0
												Trail_width[Leader,Leader_y_position+1]=1.0
												Calling_to_go[Leader]==0.0
												if Follower_ant[Leader]!=0:
													Trail_width[ant,Leader_y_position]=0.0
													Trail_width[ant,Leader_y_position+1]=1.0
										elif coin_toss_move_y>prob_down:
											if Leader_y_position-1 not in y_position_same_x:
												Trail_width[Leader,Leader_y_position]=0.0
												Trail_width[Leader,Leader_y_position-1]=1.0
												Calling_to_go[Leader]==0.0
												if Follower_ant[Leader]!=0:
													Trail_width[ant,Leader_y_position]=0.0
													Trail_width[ant,Leader_y_position-1]=1.0
								elif position_TL[0]<=90 and position_TL[1]>=59:
									#Parameters for one-lane experiment==============================
									probability_lost=0.7 #probablity of losing contact
									prob_unTR=1.0 #probability of unsuccessfull tandem run
									probability_interuption=0.0
									Calling_to_go[Leader]==0.0
									#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
									Trail_width[Leader,Leader_y_position]=0.0
									Trail_width[Leader,2]=1.0
									if Start_position_Leader[Leader]==0.0:
										Trail_width[ant,Leader_y_position]=0.0
										Trail_width[ant,2]=1.0
								#To check where follower is there or not and x movement
								#If it does not lost its folower
								if Lost_ant_Leader[Leader] ==0.0:
									#for measuring the number of interuption-------------------------------
									if position_TL[1]<trail_length-6 and position_TL[0]>5:
										Total_ahed_ant=np.sum(Positions[:,position_TL[1]+1])
										Total_pre_ant=np.sum(Positions[:,position_TL[0]-1])
										#if no ant is in the ahed position of the tandem leader, the she moves----------------
										if Start_position_Leader[Leader]==0 and Total_ahed_ant ==0:
											Positions[Leader,:]=Tandom_leader_movement(Positions,Start_position_Leader,Leader,Brood_transport_leader)
											ant=int(Follower_ant[Leader])
											position_FL=np.where(Positions[ant,:]==1)[0]
											if ant!=0:
												behind_follower_ant=np.where(Positions[:,position_FL[0]-1]==1)[0] 
											elif ant==0:
												#Since the leader move one step
												behind_follower_ant=np.where(Positions[:,position_TL[0]]==1)[0] 
											Positions[ant,:]= Follower(position_TL,position_FL,starting,Leader,ant)
											if Define_Jam[Leader]!=0:
												Jam_length=0
												if Jaming_time[Leader]>=int(4):
													if position_TL[0]<=90 and position_TL[1]>=59:
														print(Leader,"I am the leader",Jaming_time[Leader],"My position:~~~",position_TL,'~~~~:This is resolution time %###########')
														Jamming_time_array=np.append(Jamming_time_array,Jaming_time[Leader])
													for i in range(1,len(Leaders)):
														if int(position_TL[0]-i*4)>0:
															check_position=int(position_TL[1]-i*4)
															if len(np.where(Positions[:,check_position]==1)[0])!=0:
																Jam_length +=1
															elif len(np.where(Positions[:,check_position]==1)[0]) ==0:
																Jam_affecting=np.append(Jam_affecting,Jam_length)
																break
												Define_Jam[Leader]=0
												

											interpution_Leader[Leader]=0
											interp_wait_Leader[Leader]=0
											Jaming_time[Leader]=0
											Calling_to_go[Leader]==0.0
											#=============================================================================
											#Comment:"creation of lost ant without any interruption"
											Wait_time_lost[Leader]=Wait_time_lost[Leader]+1
											coin_toss_unsuccess=np.random.uniform(0,1)
											if coin_toss_unsuccess<=0.0015:
												coin_toss_to_lost=np.random.uniform(0,1)
												#follower losing contact
												if coin_toss_to_lost<=probability_lost and Follower_ant[Leader]!=0 and Wait_time_lost[Leader]>=1*How_many_steps_one_sec:
													if ant not in Lost_ant:
														Lost_ant=np.append(Lost_ant,ant)
														Pos_lost=np.where(Positions[ant,:]==1)[0]
														Pos_lost_Leader=np.where(Positions[Leader,:]==1)[0]
														# print(ant,':~~~I am the lost ant. My position is',Pos_lost,'My leader was:~~~',Leader,'My leader position is',position_TL)
														Follower_ant[Leader]=0
														Lost_recruit_count[ant]=Leader
														Total_lost +=1
														Wait_time_lost[Leader]=0.0
											#=================================================================================

										#if no ant is in the previous position of the returning leader, then she moves----------------
										elif Start_position_Leader[Leader]==1 and Total_pre_ant ==0:
											Positions[Leader,:]=Tandom_leader_movement(Positions,Start_position_Leader,Leader,Brood_transport_leader)
											interpution_Leader[Leader]=0
											interp_wait_Leader[Leader]=0
											# print(Jaming_time[Leader],'RL')
											# Jaming_time[Leader]=0
											if Define_Jam[Leader]!=0:
												if position_TL[0]<=90 and position_TL[1]>=59:
													print(Leader,"I am the leader",Jaming_time[Leader],"My position:~~~",position_TL,'~~~~:This is resolution time 3rd way%@@@@@@@@@@')
													Jamming_time_array=np.append(Jamming_time_array,Jaming_time[Leader])
												Define_Jam[Leader]=0
												Jaming_time[Leader]=0
											Calling_to_go[Leader]==0.0
										elif Start_position_Leader[Leader]==0 and Total_ahed_ant !=0:
											# print('We are the leaders',Leaders)
											# if sum(Define_Jam)!=0:
											# 	print("@@@@@@@@~~~~~~~~~~~~~==Sad!==~~~~~~~~~~~~~~~~","+ Jam occur","~~~~~~~~~~~~~~~~~~~@@@@@@@@@@@")
											# print(Leader,"~~::My position",position_TL,'Initially','Y--possition::~~',Leader_y_position,"Starting position",Start_position_Leader[Leader])
											# if ant!=0:
											# 	print(ant,"~~::My follower",position_FL,'Initially','Y--possition::~~',follower_y_position)
											#check the other ants y poistion----------------------------------
											Leader_y_position=np.where(Trail_width[Leader,:]==1)[0][0]#y position of the leader--
											Ahead_ants=np.where(Positions[:,position_TL[1]+1]==1)[0]
											if ant!=0:
												behind_follower_ant=np.where(Positions[:,position_FL[0]-1]==1)[0] 
											if ant==0:
												behind_follower_ant=np.where(Positions[:,position_TL[0]-1]==1)[0] 
											y_position_ahed_ant_array=np.zeros(len(Ahead_ants))
											count_ahead_ant=0
											
											for ahed_ant in Ahead_ants:
												y_position_ahed_ant=np.where(Trail_width[ahed_ant,:]==1)[0][0]
												y_position_ahed_ant_array[count_ahead_ant]=y_position_ahed_ant
												count_ahead_ant +=1

												
												#Recruiting ahed ant---------------------------------------------------------------------------
												if y_position_ahed_ant==Leader_y_position:
													if ahed_ant in Lost_ant and Follower_ant[Leader]==0 and Brood_transporter_ant[Leader]==0.0:
														coin_toss_take_lost=np.random.uniform(0,1)
														if coin_toss_take_lost<=prob_lost_taken:
															Follower_ant[Leader]=ahed_ant
															Start_position_Leader[Leader]=0.0
															if Leader!=Lost_recruit_count[ahed_ant]:
																Total_MR +=1
															# Jam_Creating_Leader[pre_ant]=1
															Lost_recruit_count[ahed_ant]=-1

															Calling_to_go[Leader]=0.0
															Calling_to_go[ahed_ant]=0.0
															Lost_ant=np.delete(Lost_ant,np.where(Lost_ant==ahed_ant))
															Pos_lost=np.where(Positions[ahed_ant,:]==1)[0]
															# print('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@ taken by a leader who is moving towards the new nest @@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
															# print(ahed_ant,':~~~I have been taken by the leader:~~',Leader,'. My position was~~',Pos_lost, 'My saviour position is',position_TL)
															Pos_lost_Leader=np.where(Positions[Leader,:]==1)[0]
															Pos_lost_ant=np.where(Positions[ahed_ant,:]==1)[0]
															Positions[Leader,Pos_lost_Leader[0]]=0
															Positions[Leader,Pos_lost_Leader[1]]=0
															Positions[Leader,Pos_lost_ant[0]]=1
															Positions[Leader,Pos_lost_ant[1]]=1
															Positions[ahed_ant,Pos_lost_ant[0]]=0
															Positions[ahed_ant,Pos_lost_ant[1]]=0
															Positions[ahed_ant,Pos_lost_Leader[0]]=1
															Positions[ahed_ant,Pos_lost_Leader[1]]=1
															Pos_lost_Leader=np.where(Positions[Leader,:]==1)[0]
															Pos_lost_ant=np.where(Positions[ahed_ant,:]==1)[0]
															# print(ahed_ant,'~~~: Now my position is',Pos_lost_ant,'My leader position is',Pos_lost_Leader)
													#-------------------------------------------------------------------------------------------------------

												# print("In fornt of me there are:~~",ahed_ant,'y position',y_position_ahed_ant)
												#To check where the same x position of the ant moving in the same direction or opposite-----
												if Start_position_Leader[ahed_ant]==1:
													if y_position_ahed_ant==Leader_y_position:
														if Brood_transporter_ant[Leader]!=0 or ant!=0:
															interpution_Leader[Leader]=1
														interp_wait_Leader[Leader]=interp_wait_Leader[Leader]+1
														# print(Leader,'I am facing interruption and waits',interp_wait_Leader[Leader],"Total time elapsed",k,'x position',position_TL,'Starting position',Start_position_Leader[Leader],'y position',Leader_y_position)
														# print(ant,'I am the follower ant')
														# print(ahed_ant,'I am causing interruption','Positions',np.where(Positions[ahed_ant,:]==1)[0],'Y position',y_position_ahed_ant)
														

														# interpution_Leader[ahed_ant]=1
														###===========Jam and Interuption===========
														
														Toal_event_Jam=np.append(Toal_event_Jam,0) #possible Jamming state
														if interp_wait_Leader[Leader]==1:
															Total_encounter +=1
															coin_toss_interpt=np.random.uniform(0,1)
															if position_TL[1]>90 and position_TL[0]<59:
																if coin_toss_interpt<=probability_interuption:
																	Calling_to_go[Leader]=1.0
																	Calling_to_go[ahed_ant]=1.0
															

														if interp_wait_Leader[Leader]==int(2*How_many_steps_one_sec):
															# Num_interrption=np.append(Num_interrption,0)
															if position_TL[0]<=90 and position_TL[1]>=59 and sum(Define_Jam)==0:
																if Brood_transporter_ant[Leader]!=0 or ant!=0:
																	Total_interruption =Total_interruption +1
															# print(position_TL[0])
															# print(position_TL[0],'position',Leader,'Leader','interpution')

														if interpution_Leader[Leader]!=0 and sum(Define_Jam)==0:
															# print(Leader,'I still in jam counting time',Jaming_time[Leader])
															if len(behind_follower_ant)!=0:
																if int(behind_follower_ant[0]) in Leaders:																										
																	Jaming_time[Leader]=Jaming_time[Leader]+1/How_many_steps_one_sec
																if Jaming_time[Leader]>=int(4):
																	# Toal_event_Jam[-1]=1.0
																	if sum(Define_Jam)==0:
																		# print( Jaming_time[Leader])
																		# print("@@@@@@@@~~~~~~~~~~~~~==Sad!==~~~~~~~~~~~~~~~~","+ Jam occur","~~~~~~~~~~~~~~~~~~~@@@@@@@@@@@")
																		# print(Leader,'~~:I am the jam creating leader. My position is',position_TL,'My follower is',ant)
																		# print(ant,'~~~~~: I am the follower. My position is',position_FL)
																		# for behind_ant in behind_follower_ant:
																		# 	pos_behind=np.where(Positions[behind_ant,:])[0]
																		# 	print(behind_ant,"I am the behind ant. My position is",pos_behind,'My follower is',Follower_ant[behind_ant])
																		
																		Define_Jam[Leader]=1.0
																		# Define_Jam[ahed_ant]=1.0
																		if position_TL[0]<=90 and position_TL[1]>=59:
																			Total_Jam = Total_Jam +1
														#This line for those events: After occuring a jam the condition of jam does not follow then
														if Define_Jam[Leader]==1:
															Jaming_time[Leader]=Jaming_time[Leader]+1/How_many_steps_one_sec


														
														if Define_Jam[Leader]==0 and interp_wait_Leader[Leader]>=int(4.0*How_many_steps_one_sec):
															coin_toss_unsuccess=np.random.uniform(0,1)
															if coin_toss_unsuccess<=prob_unTR:
																coin_toss_to_lost=np.random.uniform(0,1)
																#follower losing contact
																if coin_toss_to_lost<=probability_lost and Follower_ant[Leader]!=0:
																	if ant not in Lost_ant:
																		Lost_ant=np.append(Lost_ant,ant)
																		Pos_lost=np.where(Positions[ant,:]==1)[0]
																		Pos_lost_Leader=np.where(Positions[Leader,:]==1)[0]
																		# print(ant,':~~~I am the lost ant. My position is',Pos_lost,'My leader was:~~~',Leader,'My leader position is',position_TL)
																		Follower_ant[Leader]=0
																		Lost_recruit_count[ant]=Leader
																		Total_lost +=1
																		# Lost_recruit_count=np.append(Lost_recruit_count,ant)
																		
																	# Lost_ant_Leader[Leader]=ant
																	
																	
																#switching over
																elif coin_toss_to_lost>probability_lost and ant!=0:
																	Start_position_Leader[Leader]=1
																	Start_position_Leader[ahed_ant]=0
																	Follower_ant[ahed_ant]=ant
																	Follower_ant[Leader]=0
																	
																	# print(ant,'!!!! I switch my leader from',Leader,'to',ahed_ant)
																	
																	if Switchingover_count[ant]==0:
																		Total_swtovr +=1
																		Total_swtovr_no_jam+=1
																		Switchingover_count[ant]=1
																	# print(Total_swtovr)
																	# Num_interrption[-1]=Num_interrption[-1]+1
																	Pos_swor_Leader=np.where(Positions[Leader,:]==1)[0]
																	Pos_swor_ant=np.where(Positions[ant,:]==1)[0]
																	# print(ant,'My position was',Pos_swor_ant,'My leader was',Leader, 'her position was',Pos_swor_Leader)
																	Positions[Leader,Pos_swor_Leader[0]]=0
																	Positions[Leader,Pos_swor_Leader[1]]=0
																	Positions[Leader,Pos_swor_ant[0]]=1
																	Positions[Leader,Pos_swor_ant[1]]=1
																	Positions[ant,Pos_swor_ant[0]]=0
																	Positions[ant,Pos_swor_ant[1]]=0
																	Positions[ant,Pos_swor_Leader[0]]=1
																	Positions[ant,Pos_swor_Leader[1]]=1
																	Pos_swor_Leader=np.where(Positions[Leader,:]==1)[0]
																	Pos_swor_ant=np.where(Positions[ant,:]==1)[0]
																	# print(ant,'My position is',Pos_swor_ant,'My leader is',Leader, 'her position is',Pos_swor_Leader)
																	# print(ant,':~~~I am the Switchover ant. My position is',Pos_swor,'My leader was:~~~',Leader,'My leader position is',position_TL)
																	# Pos_ah=np.where(Positions[ahed_ant,:]==1)[0]
																	# print('My new leader is',ahed_ant,'Her position is',Pos_ah)
																
														# Waiting_time_switch_over=np.zeros(number_ant)
														if Define_Jam[Leader]==1:
															# Jam_Leader=np.where(Define_Jam==1)[0]
															# Waiting_time_switch_over[Leader] =Waiting_time_switch_over[Leader]+1
															if interp_wait_Leader[Leader]>=int(9.0*How_many_steps_one_sec):
																coin_toss_unsuccess=np.random.uniform(0,1)
																if coin_toss_unsuccess<=prob_unTR:
																	coin_toss_to_lost=np.random.uniform(0,1)
																	#follower losing contact
																	if coin_toss_to_lost<=probability_lost and ant!=0:
																		# print('lost holo',ant)
																		if ant not in Lost_ant:
																			Lost_ant=np.append(Lost_ant,ant)
																			Pos_lost=np.where(Positions[ant,:]==1)[0]
																			# print(ant,':~~~I am the lost ant. My position is',Pos_lost,'My leader was:~~~',Leader,'My leader position is',position_TL)
																			Follower_ant[Leader]=0
																			Lost_recruit_count[ant]=Leader
																			Total_lost +=1
																		# Lost_ant_Leader[Leader]=ant
																		
																		
																		
																	#switching over
																	elif coin_toss_to_lost>probability_lost and Follower_ant[Leader]!=0:
																		Start_position_Leader[Leader]=1
																		Start_position_Leader[ahed_ant]=0
																		Follower_ant[ahed_ant]=ant
																		Follower_ant[Leader]=0
																		# print(ant,'!!!! I switch my leader from',Leader,'to',ahed_ant)
																		
																		if Switchingover_count[ant]==0:
																			Total_swtovr +=1
																			Total_swtovr_jam+=1
																			Switchingover_count[ant]=1
																		# print(Total_swtovr)
																		# Num_interrption[-1]=Num_interrption[-1]+1
																		Pos_swor_Leader=np.where(Positions[Leader,:]==1)[0]
																		Pos_swor_ant=np.where(Positions[ant,:]==1)[0]
																		# print(ant,'My position was',Pos_swor_ant,'My leader was',Leader, 'her position was',Pos_swor_Leader)
																		Positions[Leader,Pos_swor_Leader[0]]=0
																		Positions[Leader,Pos_swor_Leader[1]]=0
																		Positions[Leader,Pos_swor_ant[0]]=1
																		Positions[Leader,Pos_swor_ant[1]]=1
																		Positions[ant,Pos_swor_ant[0]]=0
																		Positions[ant,Pos_swor_ant[1]]=0
																		Positions[ant,Pos_swor_Leader[0]]=1
																		Positions[ant,Pos_swor_Leader[1]]=1
																		Pos_swor_Leader=np.where(Positions[Leader,:]==1)[0]
																		Pos_swor_ant=np.where(Positions[ant,:]==1)[0]
																		# print(ant,'My position is',Pos_swor_ant,'My leader is',Leader, 'her position is',Pos_swor_Leader)
																		# print(ant,':~~~I am the Switchover ant. My position is',Pos_swor,'My leader was:~~~',Leader,'My leader position is',position_TL)
																		# Pos_ah=np.where(Positions[ahed_ant,:]==1)[0]
																		# print('My new leader is',ahed_ant,'Her position is',Pos_ah)
																
																
											
											#x movement of the leader---------------------

											if position_TL[1]>=90 or position_TL[1]<58:
												# print('~~~~~~~~dukeche~~~~~~~~~~')
												if Leader_y_position not in y_position_ahed_ant_array:
													# print(Leader,'I do not see anyone in my path',position_TL)
													Positions[Leader,:]=Tandom_leader_movement(Positions,Start_position_Leader,Leader,Brood_transport_leader)
													ant=int(Follower_ant[Leader])
													position_FL=np.where(Positions[ant,:]==1)[0]
													Positions[ant,:]= Follower(position_TL,position_FL,starting,Leader,ant)
													
													if Define_Jam[Leader]!=0:
														if position_TL[0]<=90 and position_TL[1]>=59:
															print(Leader,"I am the leader",Jaming_time[Leader],"My position:~~~",position_TL,'~~~~:This is resolution time 2nd way%###########')
															Jamming_time_array=np.append(Jamming_time_array,Jaming_time[Leader])
														# print(Jaming_time[Leader],'TL')
														# print(Leader,"I am the leader",Jaming_time[Leader],'~~~~:This is resolution time %###########','2nd way',position_TL)
														Define_Jam[Leader]=0
														Jaming_time[Leader]=0
														
													if interpution_Leader[Leader]!=0:
														interpution_Leader[Leader]=0
														interp_wait_Leader[Leader]=0
													Calling_to_go[Leader]==0.0
												# print('dukeche')
												# print(Leader,"~~::My position",position_TL,'Finally')


											# elif Leader_y_position in y_position_ahed_ant_array:
											# 	if interpution_Leader[Leader]!=0:
											# 		print(position_TL[0],'position',interp_wait_Leader[Leader],'time',Leader,'Leader','TL wait')

										# For returning leader if ant presents in previous position---------------------------------------
										elif Start_position_Leader[Leader]==1 and Total_pre_ant !=0:
											# print(Leader,"~~::My position",position_TL,'Initially','Y--possition::~~',Leader_y_position,"Starting position",Start_position_Leader[Leader])
											# print(ant,"~~::My follower",position_FL,'Initially','Y--possition::~~',follower_y_position)
											#check the other ants y poistion----------------------------------
											Leader_y_position=np.where(Trail_width[Leader,:]==1)[0][0]#y position of the returning leader--
											Previous_ants=np.where(Positions[:,position_TL[0]-1]==1)[0]#x position of the leader who is in the previous position--
											y_position_pre_ant_array=np.zeros(len(Previous_ants))
											count_pre_ant=0
											for pre_ant in Previous_ants:
												y_position_pre_ant=np.where(Trail_width[pre_ant,:]==1)[0][0]
												y_position_pre_ant_array[count_pre_ant]=y_position_pre_ant
												Pos_pre=np.where(Positions[pre_ant,:]==1)[0]
												# print(Leader,"In fornt of me there are:~~",pre_ant,'x position',Pos_pre,'y position',y_position_pre_ant,'starting position',Start_position_Leader[pre_ant])
												# if returning leader find a lost ant in path she will take the lost ant to the new nest
												if pre_ant in Lost_ant:
													coin_toss_take_lost=np.random.uniform(0,1)
													
													if y_position_pre_ant==Leader_y_position and coin_toss_take_lost<=prob_lost_taken:
														Follower_ant[Leader]=pre_ant
														Start_position_Leader[Leader]=0.0
														Calling_to_go[Leader]==0.0
														Calling_to_go[pre_ant]==0.0
														# print(Leader,'This is current leader. This was my leader',Lost_recruit_count[pre_ant])
														if Leader!=Lost_recruit_count[pre_ant]:
															Total_MR +=1
															# print('This is an event of midway recruitment.')
														# Jam_Creating_Leader[pre_ant]=1
														Lost_recruit_count[pre_ant]=-1
														Lost_ant=np.delete(Lost_ant,np.where(Lost_ant==pre_ant))
														Pos_lost=np.where(Positions[pre_ant,:]==1)[0]
														# print(pre_ant,':~~~I have been taken by the leader:~~',Leader,'. My position was~~',Pos_lost, 'My saviour position is',position_TL)
												count_pre_ant +=1

											#Leader x movement
											if position_TL[0]>91 or position_TL[0]<=59:
												# print('~~~~~~~~dukeche~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~++++++',sum(New_nest))
												# print()
												if Leader_y_position not in y_position_pre_ant_array:
													# print(Leader,'I do not see anyone in my path',position_TL)
													Positions[Leader,:]=Tandom_leader_movement(Positions,Start_position_Leader,Leader,Brood_transport_leader)
													Waiting_time_ahed_ant[Leader]=0
													Calling_to_go[Leader]==0.0
													if Define_Jam[Leader]!=0:
														if position_TL[0]<=90 and position_TL[1]>=59:
															print(Leader,"I am the leader",Jaming_time[Leader],"My position:~~~",position_TL,'~~~~:This is resolution time 4th way%###########')
															Jamming_time_array=np.append(Jamming_time_array,Jaming_time[Leader])
														Define_Jam[Leader]=0
														Jaming_time[Leader]=0

												# if interpution_Leader[Leader]!=0:
												# 	print(position_TL[0],'position',interp_wait_Leader[Leader],'time',Leader,'Leader',"RL")

													interpution_Leader[Leader]=0
													interp_wait_Leader[Leader]=0
												#checking for moving backword
												# Check_y_position=y_position_pre_ant_array
											elif position_TL[0]<=91 and position_TL[0]>59:
												y_position_pre_ant_array=np.array([0,1,2,3,4]) #This is because the ant

											if Leader_y_position in y_position_pre_ant_array:
												
												Waiting_time_ahed_ant[Leader]=Waiting_time_ahed_ant[Leader]+1
												# print(Previous_ants[0],'I am the leader who causes interruption and:~~~~',Leader,'~~~~I am the otherone.  We waited for',Waiting_time_ahed_ant[Leader])
												if Define_Jam[Previous_ants[0]]==0:
													if Waiting_time_ahed_ant[Leader]>=4.0*How_many_steps_one_sec and Start_position_Leader[Previous_ants[0]]==0:
														
														coin_toss_to_move_back=np.random.uniform(0,1)
														if coin_toss_to_move_back<=prob_back:
															Start_position_Leader[Leader]=0
															Waiting_time_ahed_ant[Leader]=0
															# print("@@@@@@@@~~~~~~~~~~~~~==Wow!==~~~~~~~~~~~~~~~~","+ Interpution resolved","~~~~~~~~~~~~~~~~~~~@@@@@@@@@@@")
														interpution_Leader[Leader]=0
														interp_wait_Leader[Leader]=0
												if Define_Jam[Previous_ants[0]]==1:
													# print(Previous_ants[0],'I am the leader who causes jam and:~~~~',Leader,'~~~~I am the otherone. We waited for',Jaming_time[Previous_ants[0]],'Total time ellapsed',k)

													if Waiting_time_ahed_ant[Leader]>=9*How_many_steps_one_sec and Start_position_Leader[Previous_ants[0]]==0:
														coin_toss_to_move_back=np.random.uniform(0,1)
														if coin_toss_to_move_back<=prob_back_jam:
															# print(Previous_ants[0],'I am the leader who causes jam and:~~~~',Leader,'~~~~I am the otherone.')
															Start_position_Leader[Leader]=0
															Waiting_time_ahed_ant[Leader]=0
															# print("@@@@@@@@~~~~~~~~~~~~~==Wow!==~~~~~~~~~~~~~~~~","+ Jam Resolved","~~~~~~~~~~~~~~~~~~~@@@@@@@@@@@")

									else:
										Positions[Leader,:]=Tandom_leader_movement(Positions,Start_position_Leader,Leader,Brood_transport_leader)
										Calling_to_go[Leader]==0.0
										if Define_Jam[Leader]!=0:
											if position_TL[0]<=90 and position_TL[1]>=59:
												print(Leader,"I am the leader",Jaming_time[Leader],"My position:~~~",position_TL,'~~~~:This is resolution time 5th way%###########')
												Jamming_time_array=np.append(Jamming_time_array,Jaming_time[Leader])
											Define_Jam[Leader]=0
											Jaming_time[Leader]=0
										ant=int(Follower_ant[Leader])
										if ant !=0:
											# ant=int(Follower_ant[Leader])
											position_FL=np.where(Positions[ant,:]==1)[0]
											Positions[ant,:]= Follower(position_TL,position_FL,starting,Leader,ant)
											
								# if Lost_ant_Leader[Leader]==0.0 and Calling_to_go[Leader]!=0.0:
								# 	coin_toss_ending_call=np.random.uniform(0,1)
								# 	interp_wait_Leader[Leader]=interp_wait_Leader[Leader]+1
								# 	if coin_toss_ending_call<=probability_ending_call:
								# 		Calling_to_go[Leader]=0.0
								# 		if interp_wait_Leader[Leader]==int(2*How_many_steps_one_sec):
								# 			Total_interruption+=1
								# 	if interpution_Leader[Leader]!=0:
								# 		if len(behind_follower_ant) !=0:
								# 			if int(behind_follower_ant[0]) in Leaders:
								# 				if ant !=0:
								# 					# print(behind_follower_ant,'waiting leader',Leader,'Leader',ant)
								# 					# print(Jaming_time[Leader],'waiting time')
								# 					Jaming_time[Leader]=Jaming_time[Leader]+1
								# 					if Jaming_time[Leader]==int(4*How_many_steps_one_sec):
								# 						# Toal_event_Jam[-1]=1.0
								# 						if sum(Define_Jam)==0:
								# 							Define_Jam[Leader]=1.0
								# 							Total_Jam = Total_Jam +1
								

								#searching for lost leader
								# ant=int(Follower_ant[Leader])
								# if Lost_ant_Leader[Leader]!=0.0:
								# 	Lost_searching_time[Leader]=Lost_searching_time[Leader]+1.0
								# 	#search for 6 sec
								# 	if Lost_searching_time[Leader]<=6.0:
								# 		position_TL=np.where(Positions[Leader,:]==1)[0]
								# 		Positions[Leader,:]=movement_lost_ant(position_TL,Leader)
								# 		searching_leader_position=np.where(Positions[Leader,:]==1)[0]
								# 		lost_follower_ant=int(Lost_ant_Leader[Leader])
								# 		position_lost_ant=np.where(Positions[lost_follower_ant,:]==1)[0]
								# 		#finding lost follower-------------------------------------------
								# 		# if abs(position_lost_ant[1]-searching_leader_position[0])==1.0 and Lost_searching_time[Leader]>3.0:
								# 		# 	Follower_ant[Leader]=lost_follower_ant
								# 		# 	Lost_ant_Leader[Leader]=0.0
								# 		# 	Lost_searching_time[Leader]=0.0
								# 		# 	# Jam_Creating_Leader[lost_follower_ant]=1
								# 		# 	Lost_ant=np.delete(Lost_ant,np.where(Lost_ant==lost_follower_ant))
								# 	else:
								# 		Lost_searching_time[Leader]=0.0
								# 		Lost_ant_Leader[Leader]=0.0
								# 		Start_position_Leader[Leader]=1.0
								# #reaching new nest---------------------------------------------
								ant=int(Follower_ant[Leader])
								position_FL=np.where(Positions[ant,:]==1)[0]
								position_TL=np.where(Positions[Leader,:]==1)[0]
								# print("We are the only individuals who reach to the new nest:~~",np.where(New_nest==1)[0])
								# f_ants=np.where(New_nest==1)[0]
								# for f_ant in f_ants:
								# 	print(f_ant,'I am the new nest ant',np.where(Positions[f_ant,:]==1)[0])
								if position_FL[1]==trail_length-3 and position_TL[1]==trail_length-1 and ant !=0:
									# print(position_FL[1])
									position_FL=np.where(Positions[ant,:]==1)[0]
									position_TL=np.where(Positions[Leader,:]==1)[0]
									# print(position_FL,ant,'I am the follower reach to the new nest',"My leader is ",Leader,'Learder position is',position_TL)
									New_nest[ant]=1
									
									Follower_ant[Leader]=0.0
									Switchingover_count[ant]=0
									if Start_position_Leader[Leader]==0:
										Total_Tandem_Run +=1 
									Start_position_Leader[Leader]=1
									Positions[ant,position_FL[0]]=0
									Positions[ant,position_FL[1]]=0
									Positions[ant,trail_length-1]=1
									Positions[ant,trail_length-2]=1
									
									# print(Total_Tandem_Run,Leader)
									#Recruit as new leader-------------------------------------
									if ant in secondary_leader: #This line is for fixing the total number of TL
										Leaders=np.append(Leaders,ant)
									
										
									# print("We are the only individuals who reach to the new nest:~~",np.where(New_nest==1)[0],'When entered')



											
								#To terminate the tandomden leader in the new nest---------------------------
								# With out it unresolve Jam can present there--------------------------------
								
								position_TL=np.where(Positions[Leader,:]==1)[0]
								if position_TL[1]==trail_length-1 :	
									# print(Working_Leaders,'working leader')
									# print(Leaders,'Leaders')

									# print(Leaders,'leaders')
									New_nest[Leader]=1
									Brood_transporter_ant[Leader]=0
									# New_nest[ant]=1
									Lost_ant_Leader[Leader]=0.0
									if Leader in primary_Leadr:
										primary_Leadr=np.delete(primary_Leadr,np.where(primary_Leadr==Leader))
										Start_position_Leader[Leader]=1.0
									elif Leader not in primary_Leadr:
										Start_position_Leader[Leader]=1.0

									if Leader not in secondary_leader:
										Start_position_Leader[Leader]=1.0
											
									elif Leader in secondary_leader:
										Examining_time[Leader]=Examining_time[Leader]+1
										if Examining_time[Leader]>=Random_Examining_time[Leader]*60*How_many_steps_one_sec:
											# print("I was a secondary leader:~"+str(Leader)+"I waited here:~~"+str(Examining_time[Leader]/(60*8)))
											Start_position_Leader[Leader]=1.0
											secondary_leader=np.delete(secondary_leader,np.where(secondary_leader==Leader))
											
											
											
											# print(secondary_leader,Examining_time[Leader],Leader)
										
									#Leader end the journey of leder in the new nest-------------------------
									if Num_Tandem_Run[Leader]>=1 and len(Working_Leaders)>1:
										if Leader not in primary_Leadr:
											if Leader not in secondary_leader:
												coin_toss_not_be_a_Leader=np.random.uniform(0,1)
												if coin_toss_not_be_a_Leader<=probability_not_Leader:
													# print('@@@@@@@@~~~~~~~~~~~~~~~~~~~~~~I sadly announce that I have been deleted as a leader~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~@@@@@@@@')
													Start_position_Leader[Leader]=0
													Leaders=np.delete(Leaders,np.where(Leaders==Leader))
													Deleted_Leaders=np.append(Deleted_Leaders,Leader)
													Positions[Leader,position_TL[0]]=0
													Positions[Leader,position_TL[1]]=0
													Positions[Leader,trail_length-1]=1
													Positions[Leader,trail_length-2]=1
													Working_Leaders=np.delete(Working_Leaders,np.where(Working_Leaders==Leader))
													# Jam_Creating_Leader[Leader]=1
											# print(Leaders)

					#counting total ant in the new nest------------------------------------------
					Total_ant_newnest=np.sum(New_nest)
	Avarge_time_required[i6]=np.sum(Time_required)/max(1, len(Time_required))
	Avarage_Interuption[i6]=np.sum(Interpution)/max(1, len(Interpution))
	Avarage_Jaming[i6]=np.sum(Jamming)/max(1, len(Jamming))
	Num_switovr_aray[i6]=(Total_swtovr)*(100/max(1.0, Total_Tandem_Run))
	Num_MR_array[i6]=(Total_MR)*(100/max(1.0, Total_Tandem_Run))
	Num_lost[i6]=Total_lost*(100/max(1.0, Total_Tandem_Run))

	Num_switovr_aray_jam[i6]=Total_swtovr_jam*(100/max(1.0, Total_Tandem_Run))
	Num_switovr_aray_no_jam[i6]=Total_swtovr_no_jam*(100/max(1.0, Total_Tandem_Run))
	print(Total_swtovr/num_sim,'Total_swtovr')
	print(Total_MR/num_sim,'Total_lost recruit')
	print(Total_Tandem_Run/num_sim,'Total tandem run')
	print(Num_switovr_aray[i6],'switchover')
	print(Num_MR_array[i6],'MR')
	print(Num_lost[i6],'lost')
	print(np.sum(Time_required)/(60*max(1, len(Time_required))),'time')
	print(np.sum(Jamming)/max(1, len(Jamming)),'Jam')
	print(np.sum(Interpution)/max(1, len(Interpution)),'Interpution')
	# print()

np.savetxt('Time_required.txt',Avarge_time_required)
np.savetxt('Interpution.txt',Avarage_Interuption)
np.savetxt('Jamming.txt',Avarage_Jaming)
np.savetxt('Number_ants.txt',Lost_taken)
np.savetxt('Jam_length.txt',Jam_affecting)
np.savetxt('Switch_over.txt',Num_switovr_aray)
np.savetxt('Lost_ant_recruit.txt',Num_MR_array)
np.savetxt('Jam_switch_over.txt',Num_switovr_aray_jam)
np.savetxt('No_jam_switch_over.txt',Num_switovr_aray_no_jam)
np.savetxt('Jamming_time.txt',Jamming_time_array)

# np.savetxt('stovr_per_interruption.txt',Num_interrption)


# Save consolidated reproducible CSV alongside Joy's original 10 .txt files
_df_out = pd.DataFrame({
    "colony_size": Lost_taken,
    "transport_time_min": Avarge_time_required / 60.0,
    "transport_time_sec": Avarge_time_required,
    "total_interruptions": Avarage_Interuption,
    "total_jams": Avarage_Jaming,
    "mr_so_pct": Num_switovr_aray,
    "mr_lf_pct": Num_MR_array,
    "total_mr_pct": Num_switovr_aray + Num_MR_array,
    "lost_pct": Num_lost,
    "mr_so_jam_pct": Num_switovr_aray_jam,
    "mr_so_no_jam_pct": Num_switovr_aray_no_jam,
})
_df_out.to_csv(_args.output, index=False)
