import aria2p
import subprocess
import asyncio
import os
import random
from flask import Flask, render_template, request, redirect, make_response, session,url_for,send_from_directory
app = Flask(__name__)

#how too get environment varible values -->  " os.environ['S3_KEY'] "
aria2 = aria2p.API(
        aria2p.Client(
            host="http://localhost",
            port=6800,
            secret=""
        )
    )

@app.route('/run',methods = ['GET'])
def run():
    aria2_daemon_start_cmd = []
    aria2_daemon_start_cmd.append("aria2c")
    aria2_daemon_start_cmd.append("--daemon=true")
    aria2_daemon_start_cmd.append("--enable-rpc")
    aria2_daemon_start_cmd.append("--follow-torrent=mem")
    aria2_daemon_start_cmd.append("--max-connection-per-server=10")
    aria2_daemon_start_cmd.append("--min-split-size=10M")
    aria2_daemon_start_cmd.append("--rpc-listen-all=false")
    aria2_daemon_start_cmd.append("--rpc-listen-port=6800")
    aria2_daemon_start_cmd.append("--rpc-max-request-size=1024M")
    aria2_daemon_start_cmd.append("--seed-ratio=0.0")
    aria2_daemon_start_cmd.append("--seed-time=1")
    aria2_daemon_start_cmd.append("--split=10")
    aria2_daemon_start_cmd.append("--bt-stop-timeout=600")
    aria2_daemon_start_cmd.append("--dir=/app/static/files")
    aria2_daemon_start_cmd.append("--dir=/Users/pradeepjangid/torgram_projects/torgram/static/files")
    subprocess.Popen(aria2_daemon_start_cmd)
    subprocess.call
    return redirect(url_for('home'))

@app.route('/',methods = ['GET'])
def home():
    uid_token = request.cookies.get('uid_token')
    if 'aria2c' in str(subprocess.Popen(['ps -ax'],shell=True,stdout=subprocess.PIPE).stdout.read()).replace('\n','<br>'):
        downloads = aria2.get_downloads()
        opt=[]
        for download in downloads:
            tmp=[]
            tmp.append(str(download.name))
            tmp.append(str(download.download_speed_string()))
            tmp.append(str(download.total_length_string()))
            tmp.append(str(download.connections))
            tmp.append(str(download.progress_string()))
            if str(download.status)=='active':
                tmp.append('bg-success progress-bar-striped progress-bar-animated')
            elif str(download.status)=='complete':
                tmp.append('progress-bar-info')
            else:
                tmp.append('bg-danger progress-bar-striped')
            tmp.append(str(download.eta_string()))
            tmp.append(str(download.gid))
            opt.append(tmp)
        if uid_token:
            remote_list=str(subprocess.check_output("rclone listremotes", shell=True)).replace("b'","").replace("'","").split(":\\n")[:-1]
            if uid_token in remote_list:
                return render_template('index.html',opt=opt,login=uid_token)
            else:
                return render_template('index.html',opt=opt,login="false")
        else:
            return render_template('index.html',opt=opt,login="false")
    else:
        return redirect(url_for('run'))

@app.route('/list',methods = ['GET'])
def list():
    # list all downloads
    downloads = aria2.get_downloads()
    opt=''
    for download in downloads:
        opt=opt+'Name : '+str(download.name)+'<br>'
        opt=opt+'D Speed : '+str(download.download_speed_string())+'<br>'
        opt=opt+'Total : '+str(download.total_length_string())+'<br>'
        opt=opt+'Seeds and peers  : '+str(download.connections)+'<br>'
        opt=opt+'Progress : '+str(download.progress_string())+'<br>'
        opt=opt+'status : '+str(download.status)+'<br>'
        opt=opt+'ETA : '+str(download.eta_string())+'<br><hr>'
    return str(opt)

# to pause leech with gid
@app.route('/pause',methods = ['GET'])
def pause():
    gid = request.args.get('gid')
    tmp = aria2.get_download(gid)
    if tmp.status=='paused':
        return 'False'
    else:
        tmp.pause()
        return 'True'

# to resume leech of specific gid
@app.route('/resume',methods = ['GET'])
def resume():
    gid = request.args.get('gid')
    tmp = aria2.get_download(gid)
    if tmp.status=='active':
        return 'False'
    else:
        tmp.resume()
        return 'True'

# to stop/remove leech of specific gid 
@app.route('/stop',methods = ['GET'])
def stop():
    gid = request.args.get('gid')
    tmp = aria2.get_download(gid)
    if tmp.status=='active' or 'paused':
        tmp.remove()
        return 'True'
    else:
        return 'False'

# Status of download of specific leech with gid input ( here gid is of parent data)
@app.route('/status',methods = ['GET'])
def status():
    gid = request.args.get('gid')
    new_gid=aria2.get_download(gid).followed_by_ids[0]
    file = aria2.get_download(new_gid)
    opt=''
    opt=opt+'Name: '+str(file.name)+'<br>'
    opt=opt+'Speed: '+str(file.download_speed_string())+'<br>'
    opt=opt+'D Speed: '+str(file.download_speed_string())+'<br>'
    opt=opt+'U Speed: '+str(file.upload_speed_string())+'<br>'
    opt=opt+'Progress: '+str(file.progress_string())+'<br>'
    opt=opt+'Total: '+str(file.total_length_string())+'<br>'
    return opt


@app.route('/upload',methods = ['GET'])
def upload():
    return render_template('upload.html')

# add magnet link to Aria2C 
@app.route('/add-magnet',methods = ['GET'])
def download():
    magnet_uri = request.args.get('mag-link')
    gid = aria2.add_magnet(magnet_uri).gid
    return str(gid)


# to list drive  sub folder.. 
@app.route('/drive/<arg>',methods = ['GET'])
def action(arg):
        sel_dr= request.args.get('drive')
        arg1=str(arg).replace('|','/')
        arg=arg+'|'
        ls1=[]
        ls2=[]
        ls3=[]
        ls4=[]
        #properties extract i.e folder or file
        tmp1=[]
        k=subprocess.Popen(["ls","-l","static/files/"+arg1],stdout=subprocess.PIPE).stdout
        for i in k:
            tmp1.append(str(i))
        tmp1=tmp1[1:]
        for i in tmp1:
            ls1.append(str(i).split("'")[1][0])
        #seq. me name load from system
        tmp2=[]
        k=subprocess.Popen(["ls","static/files/"+arg1],stdout=subprocess.PIPE).stdout
        for i in k:
            tmp2.append(str(i))
        for i in tmp2:
            ls2.append(str(i).split("'")[1].split("\\n")[0])
        #diffrent lists of files and folders
        for i in range(0,len(ls1)):
            if ls1[i]=='d':
                ls3.append(ls2[i])
            elif ls1[i]=='-':
                ls4.append(ls2[i])
        arg1=arg1+'/'
        return render_template('drive.html',list1=ls3,list2=ls4,arg=arg,arg1=arg1,d_name=sel_dr)

# copy file to remote drive function ...
@app.route('/m2d',methods = ['GET'])
def copy2d():
    sel_dr = request.args.get('drive')
    k = request.args.get('k')
    path=str(k).replace('|','/').replace(' ','\ ').replace('[','\[').replace(']','\]').replace('(','\(').replace(')','\)')
    if sel_dr:
        process = subprocess.Popen(['nohup rclone copy static/files/'+path+' '+sel_dr+':/drive -P > static/files/logs/'+str(path.split('/')[-1])+'-logfile.txt &'],shell=True,preexec_fn=os.setsid)
        return 'static/files/logs/'+str(path.split('/')[-1])+'-logfile.txt'
    else:
        process = subprocess.Popen(['nohup rclone copy static/files/'+path+' torgram:/drive -P > static/files/logs/'+str(path.split('/')[-1])+'-logfile.txt &'],shell=True,preexec_fn=os.setsid)
        return str('nohup rclone copy static/files/'+path+' torgram:/drive -P > static/files/logs/'+str(path.split('/')[-1])+'-logfile.txt &')

# all drive stransfer in system
@app.route('/drive-transfers',methods = ['GET'])
def drive_transfers():
        files_list=[str(i).split("'")[1].replace("\\n","") for i in subprocess.Popen(["ls","static/files/logs"],stdout=subprocess.PIPE).stdout]
        files_list.remove('Sample Log.txt')
        lst1=[]
        for fname in files_list:
            k=open("static/files/logs/"+fname,"r").read().split("*")[-1].replace(" ","").split(",")
            lst2=[]
            #file_name-0
            lst2.append(k[0].split(":")[0])
            #transferred-1
            lst2.append(k[2].split(":")[1].replace("\t",""))
            #percentage-2
            lst2.append(k[3])
            #speed-3
            lst2.append(k[4])
            # bar color-4
            if "100%" in k[3]:
                lst2.append('bg-success progress-bar-striped progress-bar-animated')
            else:
                lst2.append('progress-bar-info')
            lst1.append(lst2)
        return render_template('drive_transfers.html',opt=lst1)


# run bash command in system
@app.route('/bash',methods = ['GET'])
def bash():
        tmp1=[]
        q = request.args.get('q')
        return str(subprocess.Popen([q],shell=True,stdout=subprocess.PIPE).stdout.read()).replace('\n','<br>')



# to list Files in drive
@app.route('/drive',methods = ['GET'])
def files():
    sel_dr= request.args.get('remote')
    ls1=[]
    ls2=[]
    ls3=[]
    ls4=[]

    #properties extract i.e folder or file
    tmp1=[]
    k=subprocess.Popen(["ls","-l","static/files"],stdout=subprocess.PIPE).stdout
    for i in k:
        tmp1.append(str(i))
    tmp1=tmp1[1:]
    for i in tmp1:
        ls1.append(str(i).split("'")[1][0])
    #seq. me name load from system
    tmp2=[]
    k=subprocess.Popen(["ls","static/files"],stdout=subprocess.PIPE).stdout
    for i in k:
        tmp2.append(str(i))
    for i in tmp2:
        ls2.append(str(i).split("'")[1].split("\\n")[0])
    #diffrent lists of files and folders
    for i in range(0,len(ls1)):
        if ls1[i]=='d':
            ls3.append(ls2[i])
        elif ls1[i]=='-':
            ls4.append(ls2[i])

    return render_template('drive.html',list1=ls3,list2=ls4,d_name=sel_dr)

# Login with rclone
@app.route('/login',methods = ['GET'])
def login():
        code = request.args.get('login_code')
        username = request.args.get('username')
        if code:
            cmd='echo "'+code+'" | rclone config create '+username+' drive config_is_local false'
            subprocess.Popen(cmd,stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.STDOUT,shell=True)
            resp = make_response(render_template('index.html',forward="true"))
            resp.set_cookie('uid_token', username)
            return resp
        else:
            username_str="user"+str(random.randrange(101, 999, 3))
            return render_template('login.html',username=username_str)



if __name__ == '__main__':
    app.run(debug=True)
