from distutils.util import execute
from doctest import master
from email import message
import tkinter as tk
import tkinter.ttk as ttk
import datetime as da
import calendar as ca
import pymysql.cursors
from tkinter import E, Toplevel, messagebox

WEEK = ['日', '月', '火', '水', '木', '金', '土']
WEEK_COLOUR = ['red', 'black', 'black', 'black','black', 'black', 'blue']
#actions = ('学校','試験', '課題', '行事', '就活', 'アルバイト','旅行')

class YicDiary:
  def __init__(self, root):
    root.title('予定管理アプリ')
    root.geometry('520x280')
    root.resizable(0, 0)
    root.grid_columnconfigure((0, 1), weight=1)
    self.sub_win = None

    self.year  = da.date.today().year
    self.mon = da.date.today().month
    self.today = da.date.today().day

    self.title = None
    # 左側のカレンダー部分
    leftFrame = tk.Frame(root)
    leftFrame.grid(row=0, column=0)
    self.leftBuild(leftFrame)

    # 右側の予定管理部分
    rightFrame = tk.Frame(root)
    rightFrame.grid(row=0, column=1)
    self.rightBuild(rightFrame)

    self.var = tk.StringVar()


  #-----------------------------------------------------------------
  # アプリの左側の領域を作成する
  #
  # leftFrame: 左側のフレーム
  def leftBuild(self, leftFrame):
    self.viewLabel = tk.Label(leftFrame, font=('', 10))
    beforButton = tk.Button(leftFrame, text='＜', font=('', 10), command=lambda:self.disp(-1))
    nextButton = tk.Button(leftFrame, text='＞', font=('', 10), command=lambda:self.disp(1))

    self.viewLabel.grid(row=0, column=1, pady=10, padx=10)
    beforButton.grid(row=0, column=0, pady=10, padx=10)
    nextButton.grid(row=0, column=2, pady=10, padx=10)

    self.calendar = tk.Frame(leftFrame)
    self.calendar.grid(row=1, column=0, columnspan=3)
    self.disp(0)


  #-----------------------------------------------------------------
  # アプリの右側の領域を作成する
  #
  # rightFrame: 右側のフレーム
  def rightBuild(self, rightFrame):
    r1_frame = tk.Frame(rightFrame)
    r1_frame.grid(row=0, column=0, pady=10)

    temp = '{}年{}月{}日の予定'.format(self.year, self.mon, self.today)
    self.title = tk.Label(r1_frame, text=temp, font=('', 12))
    self.title.grid(row=0, column=0, padx=20)

    button = tk.Button(rightFrame, text='追加', command=lambda:self.add())
    button.grid(row=0, column=1)

    self.r2_frame = tk.Frame(rightFrame)
    self.r2_frame.grid(row=1, column=0)

    '''
    r3_frame = tk.Frame(rightFrame)
    r3_frame.grid(row=2, column=0)
    chat_button = tk.Button(r3_frame, text='チャット', command=lambda:self.create_chat_widget())
    chat_button.grid(row=0, column=0)
    '''

    self.schedule()

  #-----------------------------------------------------------------
  # アプリの右側の領域に予定を表示する
  #
  def schedule(self):
    # ウィジットを廃棄
    for widget in self.r2_frame.winfo_children():
      widget.destroy()

    self.text = tk.Text(self.r2_frame, width=30, height=10)
    self.text.grid(row=1, column=1)
    scroll_v = tk.Scrollbar(self.r2_frame, orient=tk.VERTICAL, command=self.text.yview)
    scroll_v.grid(row=1, column=2, sticky=tk.N+tk.S)
    self.text["yscrollcommand"] = scroll_v.set


    # データベースに予定の問い合わせを行う
    pass
    

  #-----------------------------------------------------------------
  # カレンダーを表示する
  #
  # argv: -1 = 前月
  #        0 = 今月（起動時のみ）
  #        1 = 次月
  def disp(self, argv):
    self.mon = self.mon + argv
    if self.mon < 1:
      self.mon, self.year = 12, self.year - 1
    elif self.mon > 12:
      self.mon, self.year = 1, self.year + 1

    self.viewLabel['text'] = '{}年{}月'.format(self.year, self.mon)

    cal = ca.Calendar(firstweekday=6)
    cal = cal.monthdayscalendar(self.year, self.mon)

    # ウィジットを廃棄
    for widget in self.calendar.winfo_children():
      widget.destroy()

    # 見出し行
    r = 0
    for i, x in enumerate(WEEK):
      label_day = tk.Label(self.calendar, text=x, font=('', 10), width=3, fg=WEEK_COLOUR[i])
      label_day.grid(row=r, column=i, pady=1)

    # カレンダー本体
    r = 1
    for week in cal:
      for i, day in enumerate(week):
        if day == 0: day = ' ' 
        label_day = tk.Label(self.calendar, text=day, font=('', 10), fg=WEEK_COLOUR[i], borderwidth=1)
        if (da.date.today().year, da.date.today().month, da.date.today().day) == (self.year, self.mon, day):
          label_day['relief'] = 'solid'
        label_day.bind('<Button-1>', self.click)
        label_day.grid(row=r, column=i, padx=2, pady=1)
      r = r + 1

    # 画面右側の表示を変更
    if self.title is not None:
      self.today = 1
      self.title['text'] = '{}年{}月{}日の予定'.format(self.year, self.mon, self.today)


  #-----------------------------------------------------------------
  # 予定を追加したときに呼び出されるメソッド
  #
  def add(self):
    if self.sub_win == None or not self.sub_win.winfo_exists():
      self.sub_win = tk.Toplevel()
      self.sub_win.geometry("300x300")
      self.sub_win.resizable(0, 0)

      # ラベル
      sb1_frame = tk.Frame(self.sub_win)
      sb1_frame.grid(row=0, column=0)
      temp = '{}年{}月{}日　追加する予定'.format(self.year, self.mon, self.today)
      title = tk.Label(sb1_frame, text=temp, font=('', 12))
      title.grid(row=0, column=0)

      # 予定種別（コンボボックス）
      sb2_frame = tk.Frame(self.sub_win)
      sb2_frame.grid(row=1, column=0)
      label_1 = tk.Label(sb2_frame, text='種別 : 　', font=('', 10))
      label_1.grid(row=0, column=0, sticky=tk.W)
      self.create_schedule_category()
      self.combo = ttk.Combobox(sb2_frame, state='readonly', values=self.actions)
      self.combo.current(0)
      self.combo.grid(row=0, column=1)

      self.label_2 = tk.Label(sb2_frame, text='家族関係', font=('', 10))
      self.label_2.grid(row=0, column=2)

      self.relation = tk.Label(sb2_frame, text=self.login_info(), width=5)
      self.relation.grid(row=0, column=3)

      # テキストエリア（垂直スクロール付）
      sb3_frame = tk.Frame(self.sub_win)
      sb3_frame.grid(row=2, column=0)
      self.text = tk.Text(sb3_frame, width=40, height=15)
      self.text.grid(row=0, column=0)
      scroll_v = tk.Scrollbar(sb3_frame, orient=tk.VERTICAL, command=self.text.yview)
      scroll_v.grid(row=0, column=1, sticky=tk.N+tk.S)
      self.text["yscrollcommand"] = scroll_v.set

      # 保存ボタン
      sb4_frame = tk.Frame(self.sub_win)
      sb4_frame.grid(row=3, column=0, sticky=tk.NE)
      button = tk.Button(sb4_frame, text='保存', command=lambda:self.done())
      button.pack(padx=10, pady=10)
    elif self.sub_win != None and self.sub_win.winfo_exists():
      self.sub_win.lift()

  #-----------------------------------------------------------------
  # 予定追加ウィンドウで「保存」を押したときに呼び出されるメソッド
  #
  def done(self):
    date = f'{self.year}-{self.mon}-{self.today}'
    category = self.combo.get()
    contents = self.text.get("1.0", "end")
    
    # データベースに新規予定を挿入する
    host = '127.0.0.1'
    user = 'root'
    password = ''
    db = 'calendar'
    charset = 'utf8mb4'
    connection = pymysql.connect(host=host,
                              user=user,
                              password=password,
                              db=db,
                              charset=charset,
                              cursorclass=pymysql.cursors.DictCursor)
    try:
          connection.begin()

          with connection.cursor() as cursor:
              #cursor.execute("select * from schedule where date = '{}' and relations = '{}';".format(date, self.relation.cget("text")))
              #if len(cursor.fetchall()) != 0:   # 上書き保存
                #cursor.execute("delete from schedule where (date, relations) = ('{}', '{}')".format(date, self.relation.cget("text")))
              #if self.text == '':
                #messagebox.showinfo('warning', '未入力の項目があります')
              cursor.execute("insert into schedule(date, category, contents) values('{}', '{}', '{}')".format(date, category, contents))
              cursor.execute("select family_id from family where relation = '{}';".format(self.relation.cget('text')))
              sql1 = cursor.fetchall()[0]['family_id']
              cursor.execute("select max(schedule_id) from schedule;")
              sql2 = cursor.fetchall()[0]['max(schedule_id)']
              cursor.execute("select action_id from actions where kinds = '{}';".format(category))
              sql3 = cursor.fetchall()[0]['action_id']
              cursor.execute("insert into root(family_id, schedule_id, action_id) values('{}', '{}', '{}');".format(sql1, sql2, sql3)) 
          connection.commit()

    except Exception as e:
        print('ERROR:', e)
        connection.rollback()

    finally:
          connection.close()

    self.sub_win.destroy()


  #-----------------------------------------------------------------
  # 日付をクリックした際に呼びだされるメソッド（コールバック関数）
  #
  # event: 左クリックイベント <Button-1>
  def click(self, event):
    day = event.widget['text']
    if day != ' ':
      self.title['text'] = '{}年{}月{}日の予定'.format(self.year, self.mon, day)
      self.today = day

    host = '127.0.0.1'
    user = 'root'
    password = ''
    db = 'calendar'
    charset = 'utf8mb4'
    connection = pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=db,
                             charset=charset,
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            cursor.execute("select relation, contents, category from root join family on family.family_id = root.family_id join schedule on schedule.schedule_id = root.schedule_id where date = '{}-{}-{}';".format(self.year, self.mon, day))
            #cursor.execute("select family.relations, category as カテゴリー, contents as 内容 from schedule join family on schedule.relations=family.relations where schedule.date='{}-{}-{}';".format(self.year, self.mon, day))

            # ウェジットの削除
            self.schedule()
              
            for dict in cursor.fetchall():
              for key, value in dict.items():
                  
                  if key == 'relation':
                    self.text.insert(1.0, f'・{value}\n')
                    #ttk.Label(self.r2_frame, text=value).pack()
                  else:
                    for i in range(2, len(dict)):
                      self.text.insert(float(i), f'{key}:{value}\n')
                    #ttk.Label(self.r2_frame, text=key + ':' + value).pack()
                  #self.all_schedule.insert(float(1.0), text=key + ':' + value).grid(row=1, colmun=0)
                  

    except Exception as e:
      print('ERROR:', e)
      connection.rollback()

    finally:
        connection.close()

#--------------------------------------------------------------------------------
# ログイン時の家族関係を取得
#
  def login_info(self):
    host = '127.0.0.1'
    user = 'root'
    password = ''
    db = 'calendar'
    charset = 'utf8mb4'
    connection = pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=db,
                             charset=charset,
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            cursor.execute("select relation from family where last_name = '{}' and password = '{}';".format(name, pass_code))
            for dict in cursor:
              for key, value in dict.items():
                  return value

    except Exception as e:
      print('ERROR:', e)
      connection.rollback()

    finally:
        connection.close()

#-----------------------------------------------------------------------------
# 種別リストを作成
#
  def create_schedule_category(self):
    host = '127.0.0.1'
    user = 'root'
    password = ''
    db = 'calendar'
    charset = 'utf8mb4'
    connection = pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=db,
                             charset=charset,
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            self.actions = []
            cursor.execute("select kinds from actions")
            for dict in cursor:
              for key, value in dict.items():
                  self.actions += [value]

    except Exception as e:
      print('ERROR:', e)
      connection.rollback()

    finally:
        connection.close()

#------------------------------------------------------------------------------------
# 掲示板的な
#
'''
  def create_chat_widget(self):
    sub_r3_frame = Toplevel()
    sub_r3_frame.title('FamilyChat')
    sub_r3_frame.geometry('400x300')
    self.txt1 = tk.Text(sub_r3_frame, width=40, height=15)
    self.txt1.grid(row=0, column=0)
    scroll_v = tk.Scrollbar(sub_r3_frame, orient=tk.VERTICAL, command=self.text.yview)
    scroll_v.grid(row=0, column=1, sticky=tk.N+tk.S)
    self.text["yscrollcommand"] = scroll_v.set

    self.txt2 = tk.Text(sub_r3_frame, width=40, height=3)
    self.txt2.place(x=0, y=200)
    scroll_v = tk.Scrollbar(sub_r3_frame, orient=tk.VERTICAL, command=self.text.yview)
    scroll_v.grid(row=0, column=1, sticky=tk.N+tk.S)
    self.text["yscrollcommand"] = scroll_v.set

    btn = tk.Button(sub_r3_frame, text='送信')
    btn.grid(row=1, column=1)

  # DBに接続して、forで全履歴を取り出す。
  # 送信ボタンを押したら、DBに接続
  def transfer(self):
    pass
    
    host = '127.0.0.1'
    user = 'root'
    password = ''
    db = 'calendar'
    charset = 'utf8mb4'
    connection = pymysql.connect(host=host,
                             user=user,
                             password=password,
                             db=db,
                             charset=charset,
                             cursorclass=pymysql.cursors.DictCursor)

    try:
        with connection.cursor() as cursor:
            self.actions = []
            cursor.execute("select kinds from actions")
            for dict in cursor:
              for key, value in dict.items():
                  self.actions += [value]

    except Exception as e:
      print('ERROR:', e)
      connection.rollback()

    finally:
        connection.close()
'''

#-----------------------------------------------------------------------
# ログインクラス
#
class Login:
  def __init__(self, sub_root):
    self.create_widget(sub_root)

#-----------------------------------------------------------------------
# ログイン用ウェジット
#
  def create_widget(self, sub_root):
    sub_root.title('ログインページ')
    self.frame1 = ttk.Frame(sub_root, padding=(32))
    sub_root.protocol('WM_DELETE_WINDOW', (lambda: 'pass')())
    self.frame1.grid()

    label1 = ttk.Label(self.frame1, text='名前', padding=(10, 2))
    label1.grid(row=0, column=0, sticky=tk.E)

    self.name = tk.StringVar()
    self.name_entry = ttk.Entry(self.frame1, textvariable=self.name, width=30)
    self.name_entry.grid(row=0, column=1)

    label2 = ttk.Label(self.frame1, text='パスワード', padding=(10, 2))
    label2.grid(row=1, column=0, sticky=tk.E)

    self.password = tk.StringVar()
    self.password_entry = ttk.Entry(self.frame1, textvariable=self.password, width=30, show='*')
    self.password_entry.grid(row=1, column=1)

    buttton1 = ttk.Button(self.frame1, text='ログイン', command=lambda:self.try_login(sub_root))
    buttton1.grid(row=2, column=1, columnspan=2, sticky=tk.E)
      
    button2 = ttk.Button(self.frame1, text='新規登録はこちら', command=lambda:self.register(sub_root))
    button2.grid(row=4, column=1, sticky=tk.E)

    label3 = ttk.Label(self.frame1, text='名前とパスワードを入力して下さい', padding=(5, 2))
    label3.grid(row=3, column=0, columnspan=2, sticky=tk.E)

    label4 = ttk.Button(self.frame1, text='閉じる', command=lambda:exit())
    label4.place(x=176, y=125)

#---------------------------------------------------------------
# ログイン処理
# 
  def try_login(self, sub_root):
    host = '127.0.0.1'
    user = 'root'
    password = ''
    db = 'calendar'
    charset = 'utf8mb4'
    connection = pymysql.connect(host=host,
                              user=user,
                              password=password,
                              db=db,
                              charset=charset,
                              cursorclass=pymysql.cursors.DictCursor)

    try:
        # データが存在するか検証
        with connection.cursor() as cursor:
          global name
          name = self.name_entry.get()
          global pass_code
          pass_code = self.password.get()
          cursor.execute("SELECT * FROM family WHERE last_name='{}' AND password='{}';".format(self.name_entry.get(), self.password_entry.get()))
        
          # 認証処理
          if len(cursor.fetchall()) != 0:
            sub_root.destroy()
          else:
            messagebox.showinfo('warning', '名前またはパスワードが正しくありません')

    except Exception as e:
      print('ERROR:', e)
      connection.rollback()

    finally:
        connection.close()

#--------------------------------------------------------------------
# 新規登録
# 
  def register(self, sub_root):
    sub_win = tk.Toplevel()
    sub_win.title('新規登録')
    sub_win.geometry('400x300')
    sub_win.grab_set()
    sub_win.protocol('WM_DELETE_WINDOW', (lambda: 'pass')())

    first_name_label = ttk.Label(sub_win, text='苗字', padding=(10, 2))
    first_name_label.place(x=0, y=35)
    first_name = tk.StringVar()
    self.first_name_entry = ttk.Entry(sub_win, textvariable=first_name, width=30)
    self.first_name_entry.place(x=70, y=35)

    last_name_label = ttk.Label(sub_win, text='名前', padding=(10, 2))
    last_name_label.place(x=0, y=65)
    last_name = tk.StringVar()
    self.last_name_entry = ttk.Entry(sub_win, textvariable=last_name, width=30)
    self.last_name_entry.place(x=70, y=65)
   
    birth_label1 = ttk.Label(sub_win, text='生年月日')
    birth_label1.place(x=10, y=95)
    birth_label2 = ttk.Label(sub_win, text='年')
    birth_label2.place(x=135, y=95)
    birth_year = tk.StringVar()
    self.birth_year_entry = ttk.Entry(sub_win, textvariable=birth_year, width=10)
    self.birth_year_entry.place(x=70, y=95)

    birth_label3 = ttk.Label(sub_win, text='月')
    birth_label3.place(x=220, y=95)
    birth_mon = tk.StringVar()
    self.birth_mon_entry = ttk.Entry(sub_win, textvariable=birth_mon, width=10)
    self.birth_mon_entry.place(x=155, y=95)

    birth_label4 = ttk.Label(sub_win, text='日')
    birth_label4.place(x=310, y=95)
    birth_day = tk.StringVar()
    self.birth_day_entry = ttk.Entry(sub_win, textvariable=birth_day, width=10)
    self.birth_day_entry.place(x=245, y=95)

    relation_label = ttk.Label(sub_win, text='家族関係', padding=(10, 2))
    relation_label.place(x=0, y=125)
    relate = tk.StringVar()
    self.relate_entry = ttk.Entry(sub_win, textvariable=relate)
    self.relate_entry.place(x=70, y=125)

    password_label = ttk.Label(sub_win, text='パスワード', padding=(10, 2))
    password_label.place(x=0, y=155)
    password = tk.StringVar()
    self.password_entry = ttk.Entry(sub_win, textvariable=password)
    self.password_entry.place(x=70, y=155)

    gender_label = ttk.Label(sub_win, text='性別')
    gender_label.place(x=10, y=185)
    gender = tk.StringVar()
    self.gender_entry = ttk.Entry(sub_win, textvariable=gender)
    self.gender_entry.place(x=70, y=185)

    regist = ttk.Button(sub_win, text='登録', command=lambda:self.regist(sub_root, sub_win))
    
    regist.place(x=300, y=225)

    back_button = ttk.Button(sub_win, text='閉じる', command=lambda:self.back(sub_root, sub_win))
    back_button.place(x=300, y=255)


#-----------------------------------------------------------------
# 新規登録処理
# 
  def regist(self, sub_root, sub_win):
      # すべて入力させる
      if (self.last_name_entry.get() == ''
          or self.password_entry.get() == ''
          or self.first_name_entry.get() == ''
          or self.birth_year_entry.get() == ''
          or self.birth_mon_entry.get() == ''
          or self.birth_day_entry.get() == ''
          or self.relate_entry.get() == ''
          or self.gender_entry.get() == ''):
          messagebox.showinfo('warning', '入力されていない項目があります')
          #self.back(sub_root, sub_win)
      
      # 生年月日の項目を確認
      if (not self.birth_year_entry.get().isnumeric()
        or not self.birth_mon_entry.get().isnumeric()
        or not self.birth_day_entry.get().isnumeric()):
        messagebox.showinfo('warning', '適切な値が入力されていない項目があります')
        #self.back(sub_root, sub_win)          

          
      else:
        host = '127.0.0.1'
        user = 'root'
        password = ''
        db = 'calendar'
        charset = 'utf8mb4'
        connection = pymysql.connect(host=host,
                                user=user,
                                password=password,
                                db=db,
                                charset=charset,
                                cursorclass=pymysql.cursors.DictCursor)

        try:
          with connection.cursor() as cursor:
            cursor.execute("select * from relations where relation = '{}';".format(self.relate_entry.get()))
            if len(cursor.fetchall()) != 0:
              messagebox.showinfo('warning', 'すでに{}は登録されています'.format(self.relate_entry.get()))
              self.back(sub_root, sub_win)

            # last_name と password でDBに問い合わせて、id(pk)が複数返ってきたらback（1つだけの場合、ok）
            cursor.execute("select family_id from family where last_name='{}' and password='{};'".format(self.last_name_entry.get(), self.password_entry.get()))
            if len(cursor.fetchall()) > 0:
              messagebox.showinfo('warning', f"すでにこの'{self.last_name_entry.get()}'と'{self.password_entry.get()}'でユーザーが存在します")
              self.back(sub_root, sub_win)

        except Exception as e:
          print('ERROR:', e)

        finally:
          connection.close()

        host = '127.0.0.1'
        user = 'root'
        password = ''
        db = 'calendar'
        charset = 'utf8mb4'
        connection = pymysql.connect(host=host,
                              user=user,
                              password=password,
                              db=db,
                              charset=charset,
                              cursorclass=pymysql.cursors.DictCursor)
        try:
            connection.begin()

            with connection.cursor() as cursor:
              birth = self.birth_year_entry.get() + '-' + self.birth_mon_entry.get() + '-' + self.birth_day_entry.get()
              #sql3 = "insert into root(last_name, password) value('{}', '{}');".format(self.last_name_entry.get(), self.password_entry.get())
              cursor.execute("insert into relations values('{}', '{}');".format(self.relate_entry.get(), self.gender_entry.get()))
              cursor.execute("insert into family(last_name, password, first_name, birthday, relation) values('{}', '{}', '{}', '{}', '{}');".format(self.last_name_entry.get(), self.password_entry.get(), self.first_name_entry.get(), birth, self.relate_entry.get()))
              #cursor.execute(sql3)

            connection.commit()
            messagebox.showinfo('新規登録', '新規登録完了\n'+'ログインして下さい')
            self.back(sub_root, sub_win)

        except Exception as e:
          print('ERROR:', e)
          connection.rollback()

        finally:
            connection.close()     

#----------------------------------------------------------------------------------------
# 戻るボタン
#
  def back(self, sub_root, sub_win):
    sub_win.destroy()
    self.frame1.destroy()
    self.create_widget(sub_root)

def Main():
  sub_root = tk.Tk()
  Login(sub_root)
  sub_root.mainloop()

  root = tk.Tk()
  YicDiary(root)
  root.mainloop()

if __name__ == '__main__':
  Main()
