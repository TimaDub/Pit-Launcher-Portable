![Pit Launcher](v.1.7/assets/images/logos/icon.png)


# "Pit Launcher Portable" by Tymofii Dubovyi (Pit Corporation)

```commandline
pip install -t requirements.txt
python v.1.7/main.py
```

# Welcome to the Minecraft Launcher!  

This portable launcher is designed to help you **quickly start playing Minecraft** without the hassle of manual installation.  

---

## 🚨 Important Note  

No need to worry about installing Java — **unless you're planning to use mod loaders**.  
For mod loaders, make sure to have **Java 17 or higher** installed on your system.  

---
## 🎨 Customization

### Want to modify ? 
- If you want to customize the asset files, do it !
- Compiling the app with **Pyinstaller** using **PitLauncher.spec** the asset folder will be packed in .exe file !
But if you want to add some styles to it after compiling, 
there is another folder you can put style files :
__User/AppData/Roaming/.pit/styles/__
### Style File format ?
- To add a new style file, create a **.json** file and name it, use only small letters !
- Down below you can see an example of file !

```markdown
// all colors can be rgb(r, g, b) or hex format 
// also file supports Pyqt5 another color systems 
// example qlineargradient(), and the others !
{
    "file_name":["rgb(10, 10, 10)", // color of background
             "rgb(52, 0, 222)", // text color
             "rgb(131, 30, 232)", // button color
             "qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #3400de, stop:1 #831ee8)", // progress bar color
             "rgb(255, 255, 255)", // progress bar text color
             "rgb(52, 0, 222)", // selected tab text color
             "rgb(10, 10, 10)" // selected tab background color
        ]
}
```
- Var file_name must be the same as _file name_ !
- **blue.json** / **_"blue"_:[ ]**
- Remove **all comments** before saving !

---
Enjoy your game! 🎮✨
---

**Made by [@TimaDub](https://github.com/TimaDub)**