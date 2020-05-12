import aria2p
import subprocess
import asyncio
import os
import random
from flask import json,Flask, render_template, request, redirect, make_response, session,url_for,send_from_directory
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
    aria2_daemon_start_cmd.append("--dir=/app/drive")
    subprocess.Popen(aria2_daemon_start_cmd)
    subprocess.call
    return redirect(url_for('home'))

@app.route('/',methods = ['GET'])
def home():
    uid_token = request.cookies.get('uid_token')
    if 'aria2c' in str(subprocess.Popen(['ps -ax'],shell=True,stdout=subprocess.PIPE).stdout.read()).replace('\n','<br>'):
        return render_template("index.html")
    else:
        return redirect(url_for('run'))

#check user is  avilabe in rclone list remotes
@app.route('/check-user',methods=['GET'])
def check_user():
    username=request.args.get('username')
    user_list=[i.replace("b'","").replace("'","") for i in str(subprocess.Popen(["rclone","listremotes"], stdout=subprocess.PIPE).communicate()[0]).split(":\\n")][:-1]
    if username in user_list:
        return "true"
    else:
        return "false"


@app.route('/list',methods = ['GET'])
def list():
    # list all downloads
    downloads = aria2.get_downloads()
    result_list=[]
    for download in downloads:
        tmp={
            "Gid":str(download.gid),
            "Name":str(download.name),
            "Speed":str(download.download_speed_string()),
            "Total":str(download.total_length_string()),
            "Seeds":str(download.connections),
            "Progress":str(download.progress_string()),
            "Status":str(download.status),
            "ETA":str(download.eta_string())
        }
        result_list.append(tmp)
    output = {
        "ok": True,
        "result": result_list
        }
    response = app.response_class(
        response=json.dumps(output),
        mimetype='application/json'
    )
    return response

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
    
# add magnet link to Aria2C 
@app.route('/add-magnet',methods = ['GET'])
def download():
    magnet_uri = request.args.get('mag-link')
    gid = aria2.add_magnet(magnet_uri).gid
    return str(gid)

@app.route('/player',methods = ['GET'])
def player():
    k = request.args.get('path')
    return render_template('player.html',path=k)


# copy file to remote drive function ...
@app.route('/m2d',methods = ['GET'])
def copy2d():
    sel_dr = request.args.get('drive')
    k = request.args.get('path')
    path=str(k).replace(' ','\ ').replace('[','\[').replace(']','\]').replace('(','\(').replace(')','\)')
    if sel_dr:
        files_list=[str(i).split("'")[1].replace("\\n","") for i in subprocess.Popen(["ls","drive/logs"],stdout=subprocess.PIPE).stdout]
        if str(path.split('/')[-1])+'-'+sel_dr+'-logfile.txt' not in files_list:
            process = subprocess.Popen(['nohup rclone copy '+path+' '+sel_dr+':/drive -P > drive/logs/'+str(path.split('/')[-1])+'-'+sel_dr+'-logfile.txt &'],shell=True,preexec_fn=os.setsid)
            return '1:drive/logs/'+str(path.split('/')[-1])+'-logfile.txt'
        else:
            return '0:File Already Found In Drive'
    else:
        return "0:Drive Input Not Found"

# all drive stransfer in system
@app.route('/drive-transfers',methods = ['GET'])
def drive_transfers():
        files_list=[str(i).split("'")[1].replace("\\n","") for i in subprocess.Popen(["ls","drive/logs"],stdout=subprocess.PIPE).stdout]
        lst1=[]
        for fname in files_list:
            k=open("drive/logs/"+fname,"r").read().split("*")[-1].replace(" ","").split(",")
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

@app.route('/<path:filename>',methods=['GET'])  
def send_file(filename):
    if os.path.isdir(filename):
        remote=request.args.get('remote')
        if not remote:
            remote="false"
        path=filename+"/"
        folders=[i for i in os.listdir(path) if os.path.isdir(path+i)]
        files=[i for i in os.listdir(path) if not os.path.isdir(path+i)]
        units=[' bytes',' KB',' MB',' GB',' TB']
        human_readable= lambda bytes,units:str(bytes) + units[0] if bytes < 1024 else human_readable(bytes>>10, units[1:])
        files_size=[ human_readable(os.stat(path+i).st_size,units) for  i in files ]
        return render_template('drive.html',folders=folders,files=files,files_size=files_size,path=path,remote=remote)
    else:
        return send_from_directory("/".join(filename.split("/")[:-1]),filename.split("/")[-1])

# run bash command in system
@app.route('/bash',methods = ['GET'])
def bash():
        tmp1=[]
        q = request.args.get('q')
        return str(subprocess.Popen([q],shell=True,stdout=subprocess.PIPE).stdout.read()).replace('\n','<br>')



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
