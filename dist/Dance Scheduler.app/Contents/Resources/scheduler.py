import random

# Song properties:
class Song:
    def __init__(self, title, duration, familiarity):
        self.title = title                      # the name of the song
        self.duration = duration                # in min
        self.familiarity = familiarity          # 1 (unfamiliar) to 7 (very familiar)
        # self.desired_plays = 8 - familiarity
        self.desired_plays = familiarity        # 1 (very familiar) to 7 (unfamiliar)
        self.assigned_days = set()              # a set() of which days this song is scheduled on (0–6).

    def __repr__(self):
        return f"{self.title} ({self.duration}m, fam:{self.familiarity}, plays:{self.desired_plays})"

def decimal_minutes_to_minutes_seconds(decimal_minutes):
        """Converts decimal minutes to minutes and seconds.

        Args:
            decimal_minutes: The time in decimal minutes.

        Returns:
            A tuple containing the minutes and seconds.
        """
        minutes = int(decimal_minutes)
        seconds = int((decimal_minutes - minutes) * 60)
        return minutes, seconds

'''Constructor (this handles the scheduling logic)'''
class DanceClassScheduler:
    def __init__(self, songs, days=7, minutes_per_day=60, flexibility=2):
        self.songs = songs                                  # list of Song objects.
        self.days = days                                    # number of days in the week (default: 7).
        self.minutes_per_day = minutes_per_day              # max session time per day (60 min).
        self.flexibility = flexibility                      # give reasonable flexibility to the time constraints (50 min ~ 70 min allowed)
        self.min_minutes = minutes_per_day - flexibility
        self.max_minutes = minutes_per_day + flexibility
        self.schedule = {day: [] for day in range(days)}    # dictionary mapping each day (0–6) to a list of scheduled songs.
        self.unassigned_songs = []  # collect songs that couldn’t be fully scheduled

    # Check constraints: Total minutes used in a day:
    def total_minutes(self, day):
        return sum(song.duration for song in self.schedule[day])

    # Check constraints: All song titles already scheduled on a day:
    def song_titles(self, day):
        return [song.title for song in self.schedule[day]]

    # Main Scheduling Logic: 
    def generate_schedule(self): 
        
        # Sort songs by most desired plays first (i.e., lower familiarity scores come first)
        # songs_sorted = sorted(self.songs, key=lambda s: -s.desired_plays)

        # Tie-breaker Sorting: when two songs have the same desired plays, prioritize by longer duration or random shuffle.
        songs_sorted = sorted(self.songs, key=lambda s: (-s.desired_plays, -s.duration))

        '''Prioritizes avoiding daily duplicates and hard-stops once it can't find a valid day for a song. 
        1. You're only attempting to assign a song desired_plays times and then move on.
        2. If you can't find enough days for it (e.g., all days are full or already have that song), you abandon the song—even if the schedule is still underfilled.'''
        
        # First, sort songs so more frequently played ones are scheduled first.
        for song in songs_sorted:
            available_days = list(range(self.days)) # Get a list of all days in the week (e.g., [0, 1, 2, 3, 4, 5, 6])
            random.shuffle(available_days)  # Shuffle the list to avoid always assigning to the same early days

            plays_assigned = 0 # Keep track of how many times this song has been scheduled
                               # loop until the target number of plays is met

            while plays_assigned < song.desired_plays:
                assigned = False # haven’t scheduled this song enough times, try assigning it to days that meet the constraints
                
                for day in available_days:
                    if day in song.assigned_days:
                        continue # Don't repeat this song on the same day
                    if song.title in self.song_titles(day):
                        continue # Extra safety to prevent duplicates, avoids double-scheduling
                    
                    projected_time = self.total_minutes(day) + song.duration # checks how many minutes the day will have if this song is added
                    
                    if projected_time <= self.max_minutes: # check upper threshold
                        self.schedule[day].append(song) # Assign song to the day
                        song.assigned_days.add(day) # Track that this song is now on this day
                        plays_assigned += 1 # Count one successful play
                        assigned = True
                        break # Stop checking other days for this particular play
                
                if not assigned: # If we couldn’t find any day that works (all full or already scheduled), we give up and notify the user
                    # print(f"⚠️ Could not fully assign {song.title} (needed {song.desired_plays}, assigned {plays_assigned})")
                    self.unassigned_songs.append((song.title, song.desired_plays, plays_assigned))
                    break
        
        self.fill_underloaded_days()  # call Greedily fill after initial pass
    
    '''After the first scheduling pass (honoring desired plays), we can go back and fill up each day to min_minutes with 
       whatever remaining songs haven't yet been used that day (even if their desired play target is already met). 
       This balances both fairness and practical usage.'''
    # Greedily fill each day after initial pass: 
    def fill_underloaded_days(self):
        for day in range(self.days):
            while self.total_minutes(day) < self.min_minutes:
                added = False
                for song in self.songs:
                    if day in song.assigned_days:
                        continue
                    if song.title in self.song_titles(day):
                        continue
                    projected_time = self.total_minutes(day) + song.duration
                    if projected_time <= self.max_minutes:
                        self.schedule[day].append(song)
                        song.assigned_days.add(day)
                        added = True
                        break
                if not added:
                    break  # No more valid songs to add to this day
              

    # Print the Result:
    def print_schedule(self):
        for day in range(self.days):
            match (day+1):
                case 1:
                    print("\n📅 Monday Schedule:")
                    for song in self.schedule[day]:
                        print(f"  - {song.title} ({song.duration:.2f}m, fam: {song.familiarity})")
                        total = self.total_minutes(day)
                        total_minutes, total_seconds = decimal_minutes_to_minutes_seconds(total)
                    print(f"  Total time: {total_minutes} minutes {total_seconds} seconds")
                case 2: 
                    print("\n📅 Tuesday Schedule:")
                    for song in self.schedule[day]:
                        print(f"  - {song.title} ({song.duration:.2f}m, fam: {song.familiarity})")
                        total = self.total_minutes(day)
                        total_minutes, total_seconds = decimal_minutes_to_minutes_seconds(total)
                    print(f"  Total time: {total_minutes} minutes {total_seconds} seconds")
                case 3: 
                    print("\n📅 Wednesday Schedule:")
                    for song in self.schedule[day]:
                        print(f"  - {song.title} ({song.duration:.2f}m, fam: {song.familiarity})")
                        total = self.total_minutes(day)
                        total_minutes, total_seconds = decimal_minutes_to_minutes_seconds(total)
                    print(f"  Total time: {total_minutes} minutes {total_seconds} seconds")
                case 4: 
                    print("\n📅 Thursday Schedule:")
                    for song in self.schedule[day]:
                        print(f"  - {song.title} ({song.duration:.2f}m, fam: {song.familiarity})")
                        total = self.total_minutes(day)
                        total_minutes, total_seconds = decimal_minutes_to_minutes_seconds(total)
                    print(f"  Total time: {total_minutes} minutes {total_seconds} seconds")
                case 5: 
                    print("\n📅 Friday Schedule:")
                    for song in self.schedule[day]:
                        print(f"  - {song.title} ({song.duration:.2f}m, fam: {song.familiarity})")
                        total = self.total_minutes(day)
                        total_minutes, total_seconds = decimal_minutes_to_minutes_seconds(total)
                    print(f"  Total time: {total_minutes} minutes {total_seconds} seconds")
                case 6: 
                    print("\n📅 Saturday Schedule:")
                    for song in self.schedule[day]:
                        print(f"  - {song.title} ({song.duration:.2f}m, fam: {song.familiarity})")
                        total = self.total_minutes(day)
                        total_minutes, total_seconds = decimal_minutes_to_minutes_seconds(total)
                    print(f"  Total time: {total_minutes} minutes {total_seconds} seconds")
                case 7: 
                    print("\n📅 Sunday Schedule:")
                    for song in self.schedule[day]:
                        print(f"  - {song.title} ({song.duration:.2f}m, fam: {song.familiarity})")
                        total = self.total_minutes(day)
                        total_minutes, total_seconds = decimal_minutes_to_minutes_seconds(total)
                    print(f"  Total time: {total_minutes} minutes {total_seconds} seconds")
            if total < self.min_minutes: print(f"  ⚠️ Under min_minutes ({self.min_minutes}m)!") # under-time reporting after scheduling
            
