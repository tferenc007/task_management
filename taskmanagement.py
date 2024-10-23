import pandas as pd
import datetime
import sqlite3 as sq


# epic_df = pd.read_csv("data/epics.csv")
# stories_df = pd.read_csv("data/stories.csv")
# tasks_df = pd.read_csv("data/tasks.csv")
conn = sq.connect('data/database.db')
epic_df = pd.read_sql_query("SELECT * FROM epics", conn)
stories_df = pd.read_sql_query("SELECT * FROM stories", conn)
tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn)
conn.close()
class TaskManagement:
    def __init__(self):
            epic_ids = epic_df["id"].tolist()
            self._epics = []
            for ei in epic_ids:
                epic = Epic(epic_id=ei)
                epic.get_attr(epic_df)
                epic.get_all_stories(story_df=stories_df, task_df=tasks_df)
                self._epics.append(epic)
    @property
    def epics(self):
        return self._epics
    
    def add_task(self, task, epic_id, story_id):
        # create a new taskś
        pass

    def add_story(self, story, epic_id):
        # create a new story
        pass

    def add_epic(self, epic):
        # create a new epic
        pass

    def save(self):
        #save object to database
        pass


class Epic:
    def __init__(self, df=None, epic_id = None):
        if epic_id == None:
            self._id = df['id'].max()+1
        else:
            self._id = epic_id

        self._name = None
        self._stories = []
    @property
    def id(self):
        return self._id
    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value

    def get_all_stories(self, story_df, task_df):
        story_ids = story_df.loc[story_df["epic_id"] == self.id, "id"].tolist()
        self._stories.clear()
        for story_id in story_ids:
            my_story = Story(story_id=story_id)
            my_story.get_attr(story_df)
            my_story.get_all_tasks(task_df)
            self._stories.append(my_story)
    
    def get_attr(self, df):
        self._name = df.loc[df["id"] == self.id, "name"].squeeze() 
    @property
    def stories(self):
        return self._stories
    
class Story:
    def __init__(self, story_id):
        self._id = story_id
        self._epic_id = None
        self._tasks = []
        self._name = None
        self._description = None
        self._est_start_date = None
        self._est_end_date = None
    @property
    def tasks(self):
        return self._tasks
    @property
    def id(self):
        return self._id
    @property
    def epic_id(self):
        return self._epic_id
    @epic_id.setter
    def epic_id(self, value):
        self._epic_id = value

    @property
    def name(self):
        return self._name
    @name.setter
    def name(self, value):
        self._name = value
    
    @property
    def description(self):
        return self._description
    @description.setter
    def description(self, value):
        self._description = value

    @property
    def est_start_date(self):
        return self._est_start_date
    @ est_start_date.setter
    def est_start_date(self, value):
        try:
            # Try to parse the date and format it
            parsed_date = datetime.strptime(value, '%Y-%m-%d')
            self._est_start_date = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")


    @property
    def est_end_date(self):
        return self._est_end_date
    @ est_end_date.setter
    def est_end_date(self, value):
        try:
            # Try to parse the date and format it
            parsed_date = datetime.strptime(value, '%Y-%m-%d')
            self._est_end_date = parsed_date.strftime('%Y-%m-%d')
        except ValueError:
            raise ValueError("Date must be in YYYY-MM-DD format")
    def get_attr (self, story_df):
            check = story_df.loc[story_df["id"] == self.id, "id"]
            if check.count()==0:
                return False
            else:
                self._name = story_df.loc[story_df["id"] == self.id, "name"].squeeze()
                self._epic_id = story_df.loc[story_df["id"] == self.id, "epic_id"].squeeze()
                self._description = story_df.loc[story_df["id"] == self.id, "description"].squeeze()
                self._est_start_date = story_df.loc[story_df["id"] == self.id, "est_start_date"].squeeze()
                self._est_end_date = story_df.loc[story_df["id"] == self.id, "est_end_date"].squeeze()
                return True


    def get_all_tasks(self, df):
        task_ids = df.loc[df["story_id"] == self.id, "id"].tolist()
        self._tasks.clear()
        for task in task_ids:
            my_task = Task(task_id=task)
            my_task.get_attr(df)
            self._tasks.append(my_task)

class Task:
    def __init__(self,task_id, task_name=None, task_desc=None):
        self._stori_id = None
        self._id = task_id
        self._name = task_name
        self._description = task_desc
        self._is_completed = False
        self._complitation_date = None
        self._is_cancelled = False
    @property
    def story_id(self):
        return self._id
    
    @story_id.setter
    def story_id(self, value):
        self._story_id = value

    @property
    def id(self):
        return self._id
    
    @property
    def name(self):
        return self._name
    
    @name.setter
    def name(self,value):
        self._name=value
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self,value):
        self._description = value
    
    @property
    def is_completed(self):
        return self._is_completed
    

    @is_completed.setter
    def is_completed(self, value):
        self._is_completed = value

    @property   
    def complitation_date(self):
        return self._complitation_date
    
    @complitation_date.setter   
    def complitation_date(self, value):
        self._complitation_date = value

    @property
    def is_cancelled(self):
        return self._is_cancelled
    
    @is_cancelled.setter
    def is_cancelled(self, value):
        self._is_cancelled = value
    
    def save(self):
        # save data to db
        pass
    def get_attr(self, df):
            check = df.loc[df["id"] == self.id, "id"]
            if check.count()==0:
                return False
            else:
                self._name = df.loc[df["id"] == self.id, "name"].squeeze()
                self._story_id = df.loc[df["id"] == self.id, "story_id"].squeeze()
                self._description = df.loc[df["id"] == self.id, "description"].squeeze()
                self._is_completed = df.loc[df["id"] == self.id, "is_completed"].squeeze()
                self._is_cancelled = df.loc[df["id"] == self.id, "is_cancelled"].squeeze()
                self._complitation_date = df.loc[df["id"] == self.id, "complitation_date"].squeeze()
                return True


if __name__ =='__main__':
    # !!!!! CREATE A INNITIAL DATABASE !!!!
    # conn = sq.connect('data/database.db')
    # epic_df.to_sql('epics', conn, if_exists='replace', index=False)
    # stories_df.to_sql('stories', conn, if_exists='replace', index=False)
    # tasks_df.to_sql('tasks', conn, if_exists='replace', index=False)
    # conn.close()

# epic_df = pd.read_csv("data/epics.csv")
# stories_df = pd.read_csv("data/stories.csv")
# tasks_df = pd.read_csv("data/tasks.csv")



    e_id = 1
    s_id = 1
    t_id = 1

    epic = Epic(epic_id=e_id)
    epic.get_attr(epic_df)
    epic.get_all_stories(story_df=stories_df, task_df=tasks_df)

    tm = TaskManagement()

     
    print(f"epic: {tm.epics[0].name}")
    print(f"story: {tm.epics[0].stories[s_id-1].name}")
    print(f"task: {tm.epics[0].stories[s_id-1].tasks[t_id-1].name}")



