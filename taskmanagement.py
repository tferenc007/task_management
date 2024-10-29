import pandas as pd
from datetime import datetime, date
import sqlite3 as sq


# epic_df = pd.read_csv("data/epics.csv")
# stories_df = pd.read_csv("data/stories.csv")
# tasks_df = pd.read_csv("data/tasks.csv")


# conn = sq.connect('data/database.db')
# epic_df.to_sql('epics', conn, if_exists='replace', index=False)
# stories_df.to_sql('stories', conn, if_exists='replace', index=False)
# tasks_df.to_sql('tasks', conn, if_exists='replace', index=False)
# conn.close()

class TaskManagement:

    def __init__(self):
        conn = sq.connect('data/database.db')
        epic_df = pd.read_sql_query("SELECT * FROM epics", conn, dtype=str)
        stories_df = pd.read_sql_query("SELECT * FROM stories", conn, dtype=str)
        tasks_df = pd.read_sql_query("SELECT * FROM tasks", conn, dtype=str)
        conn.close()
        
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
    def complete_task(self, task_completed, date):
        for epic in self.epics:
            for story in epic.stories:
                for task in story.tasks:
                    if task.id == task_completed.id:
                        task.complitation_date = date
                        self.save()


    def tasks_squeeze(self, start_date=date(1900,1,1), end_date=date(2999,1,1), show_all=False):
        squeezed_tasks =[]
        for epic in self.epics:
            for stories in epic.stories:
                for task in stories.tasks:
                    #filter sections
                    if task.is_completed=='true':
                        if start_date <= datetime.strptime(task.complitation_date, "%Y-%m-%d").date():
                            if end_date >= datetime.strptime(task.complitation_date, "%Y-%m-%d").date():
                                squeezed_tasks.append(task)
                    elif show_all:
                        squeezed_tasks.append(task)
        return squeezed_tasks
    
    def stories_squeeze(self, est_start_date=date(1900,1,1), est_end_date=date(2999,1,1), is_completed=None):
        squeezed_stories = []
        for epic in self.epics:
            for story in epic.stories:
                story_est_start_date = datetime.strptime(story.est_start_date, "%Y-%m-%d").date()
                story_est_end_date = datetime.strptime(story.est_end_date, "%Y-%m-%d").date()
                if story_est_start_date>= est_start_date:
                    if story_est_end_date<=est_end_date:
                        if is_completed==None:
                            squeezed_stories.append(story)
                        if is_completed==True and story.is_completed==True:
                            squeezed_stories.append(story)
                        if is_completed==False and story.is_completed==False:
                            squeezed_stories.append(story)
        return squeezed_stories



    def last_activity(self, start_date, end_date):
        first_iteration = True
        l_activity = None
        tasks = self.tasks_squeeze(start_date=start_date, end_date=end_date)
        for task in tasks:
             comp_date = datetime.strptime(task.complitation_date, "%Y-%m-%d").date()
             if start_date <= comp_date <= end_date:
                if first_iteration:
                    first_iteration = False
                    l_activity = comp_date
                else:
                    t_date = comp_date
                    if t_date>l_activity:
                        l_activity = t_date
        return l_activity
    

    def story_count(self,  est_start_date=date(1900,1,1), est_end_date=date(2999,1,1), is_completed=None):
        stories = self.stories_squeeze(est_start_date=est_start_date, est_end_date=est_end_date, is_completed=is_completed)
        return len(stories)
    

    def task_count(self,  est_start_date=date(1900,1,1), est_end_date=date(2999,1,1), is_completed=None):
        stories = self.stories_squeeze(est_start_date=est_start_date, est_end_date=est_end_date)
        i = 0
        for story in stories:
            i = i + story.task_count(is_completed)
        return i


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

        epic_dic = []
        story_dic = []
        task_dic = []
        epics = self._epics
        for epic in epics:
            dic = {'id': epic.id, 'name': epic.name}
            epic_dic.append(dic)
            for story in epic.stories:
                s_dic = {'epic_id': story.epic_id, 'id': story.id, 'name': story.name, 'description': story.description,
                        'est_start_date': story.est_start_date, 'est_end_date': story.est_end_date}
                story_dic.append(s_dic)
                for task in story.tasks:
                    t_dic = {'story_id' : task.story_id, 'id': task.id, 'name': task.name,
                             'description': task.description, 'is_completed': task._is_completed,
                             'complitation_date': task.complitation_date, 'is_cancelled': task.is_cancelled}
                    task_dic.append(t_dic)

        e_df = pd.DataFrame(epic_dic)
        s_df = pd.DataFrame(story_dic)
        t_df = pd.DataFrame(task_dic)

        #save object to database
        conn = sq.connect('data/database.db')
        e_df.to_sql('epics', conn, if_exists='replace', index=False)
        s_df.to_sql('stories', conn, if_exists='replace', index=False)
        t_df.to_sql('tasks', conn, if_exists='replace', index=False)
        conn.close()



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
    def is_completed(self):
        is_compl = True
        for task in self.tasks:
            if task.is_completed=='false':
                is_compl = False
        return is_compl
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
    
    def task_count(self, is_completed=None):
        i = 0
        for task in self.tasks:
            if task.is_completed=='true' and is_completed==True:
                i = i + 1
            elif is_completed==None:
                i = i + 1
            elif task.is_completed=='false' and is_completed==False:
                i = i + 1            
        return i

class Task:
    def __init__(self,task_id, task_name=None, task_desc=None):
        self._stori_id = None
        self._id = task_id
        self._name = task_name
        self._description = task_desc
        self._is_completed = None
        self._complitation_date = None
        self._is_cancelled = False
    @property
    def story_id(self):
        return self._story_id
    
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

    @property   
    def complitation_date(self):
        return self._complitation_date
    
    @complitation_date.setter   
    def complitation_date(self, value):
        self._complitation_date = value
        if value !=None:
            self._is_completed = 'true'
        else:
            self._is_completed = 'false'

    @property
    def is_cancelled(self):
        return self._is_cancelled
    
    @is_cancelled.setter
    def is_cancelled(self, value):
        self._is_cancelled = value
    
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




    # print(tasks_df)
    tm = TaskManagement()
    
    for epic in tm.epics:
        for story in epic.stories:
            for task in story.tasks:
                task.complitation_date = None

    tm.save()

    # print(tm.story_count())
    # for task in tm.tasks_squeeze(show_all=True):
    #     print (task.name)

    # print (tm.last_activity())



    # print(tasks_df)

    # for epic in tm.epics:
    #     for story in epic.stories:
    #         for task in story.tasks:
    #             print(f'task id: {task.id} - story.id: {task.story_id} epic {epic.id}')

    # print(tm.epics[0].stories[0].tasks[0].complitation_date)
    # tm.epics[0].stories[0].tasks[0].complitation_date = '2024-10-25'
    # tm.epics[0].stories[0].tasks[1].complitation_date = '2024-10-24'
    # tm.epics[0].stories[0].tasks[3].complitation_date = '2024-10-20'
    # tm.epics[0].stories[0].tasks[4].complitation_date = '2024-10-21'


    # # print(tm.epics[0].stories[0].tasks[0].complitation_date)

    # print(f"epic: {tm.epics[0].name}")
    # print(f"story: {tm.epics[0].stories[s_id-1].name}")
    # print(f"task: {tm.epics[0].stories[s_id-1].tasks[t_id-1].name}")



