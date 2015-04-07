from math import *
from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.actor.Actor import Actor
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import *
from direct.gui.OnscreenImage import OnscreenImage
import sys
from direct.showbase.ShowBase import ShowBase
from direct.gui.DirectGui import *
import copy
import random
#import direct.directbase.DirectStart

cardNames=["A","2","3","4","5","6","7","8","9","10","J","Q","K"]
cardFaces=["A.png","2.png","3.png","4.png","5.png","6.png",
            "7.png","8.png","9.png","10.png","J.png","Q.png",
            "K.png"]

class MyApp(ShowBase):
    def __init__(self, fStartDirect=True):
        #ConfigVariableBool("fullscreen",0).setValue(1)
        ShowBase.__init__(self) 
        self.loadInitialCamPos()#initialize camera positioning 
        self.assocs=dict()
        self.loadBooleans()
        self.loadLists()
        self.shuffleCards()
        self.loadValues()
        #creates a random sequence of cards we will memorize 
        self.setInputs()
        #set up keyboard and mouse inputs
        self.setUpCollision()
        #sets up collision detection
        self.setUpScene()
        #sets up geometry in the 3D Enviroments
        self.loadSFX()
        self.light=self.setUpPointLight()
        taskMgr.add(self.setUpChest, 'setUpChest')
        #sets up rotating graphic of chest
        
    def loadValues(self):
        self.counter,self.lightCounter,self.fade,self.numFireflies=0,0,0,15
        self.numCards=13
        self.numCardsCopy=copy.copy(self.numCards)
        self.shuffledCardFacesCopy=copy.copy(self.shuffledCardFaces)
        
    def loadLists(self):
        self.cardsPos,self.imageList,self.visitedItems=[],[],[]
        self.buttonList,self.lastCoord,self.fireFlyList=[],[],[]
        self.previousCard,self.nextCard=[],[]
        
    def loadBooleans(self):
        self.toggleChest=False
        self.fadeToggle=False
        self.togglePreviousCard=False
        self.toggleNextCard=False
        self.toggleBar=True
        self.titleText=None
        self.userLocation=None
        
    def loadInitialCamPos(self):
        #we disable our mouse because we be using a different method
        #that will set up our mouse controls 
        base.disableMouse()
        self.camPosx,self.camPosz=15,28
        self.camera.setH(90)
        self.camera.setP(-25)
        self.heading=0
        base.camera.setPos(self.camPosx,0,self.camPosz)
        
    def loadSFX(self):
        self.soundSteps = loader.loadMusic("footsteps.wav")
        #circus in the Sky is a piece written by Uzman Riaz (credit)
        #self.circusInTheSky=loader.loadMusic("circusInTheSky.wav")
        
    def setUpCollision(self):
        #pusher and queue are handlers from when a collision occurs
        self.cTrav = CollisionTraverser()
        self.queue = CollisionHandlerQueue()
        self.pusher = CollisionHandlerPusher()
        #set up scene geometrys
        self.setUpCollisionRay()
        self.setUpCollisionNode()
        
    def setUpPointLight(self):
        taskMgr.doMethodLater(.1, self.createTitleText, 'textFadeInOut')
        #we create multiple point lights to make it appear as if there are
        #'firefly' entities within the chest 
        for n in xrange(self.numFireflies):
            self.generateLights("%fFirefly"%n)
        #sets up a soft ambient light so that our 3D enviroment appears
        #more realistic 
        self.alight = AmbientLight('ambientLight')
        self.alight.setColor(VBase4(.6, .6, .6, 1))
        alnp = render.attachNewNode(self.alight)
        render.setLight(alnp)
        self.treasureChest.setLight(alnp)

    def createTitleText(self,task):
        #task allows up to fade text in and out 
        self.updateFade()
        if self.titleText!=None:
            self.titleText.remove()
        self.titleText=OnscreenText(text="[Click on the chest to begin]",
                                    style=Plain,pos=(0,0),fg=(1,1,1,self.fade))
        if self.toggleChest==True:
            self.titleText.remove()
            return task.done
        return task.again
    
    def generateLights(self,name):
        #generate pointlights and reparenting them to the chest 
        name=PointLight("Light")
        name=render.attachNewNode(name)
        name.setPos(0,0,22)
        name.hide()
        self.modelLight = loader.loadModel("misc/Pointlight.egg.pz")
        self.modelLight.reparentTo(name)
        self.treasureChest.setLight(name)
        self.fireFlyList.append(name)
        
    def setUpChest(self,task):
        if self.toggleChest==True:
            #chest rotates backwards if clicked on
            self.speed=-1.5
        else: self.speed=.5
        #chest rotates forward slowly 
        self.lightCounter+=1
        angle,radius= radians(self.heading),1.2
        x,y,z =(cos(angle)*radius,sin(angle)*radius,sin(angle)*radius)
        self.heading+=self.speed
        self.heading%=360
        self.treasureChest.setH(self.heading)
        if self.lightCounter%7==0:
            for n in xrange(self.numFireflies):
                self.generateFireFlies(x,y,n)
        if abs(self.treasureChest.getH()-360)<2 and self.toggleChest==True:
            #if chest is activated and the chest if facing the camera 
            taskMgr.add(self.moveChest, 'moveChest')
            return task.done 
        else: return Task.cont
        
    def moveChest(self,task):
        #units are calculated so that camera and chest move simultaneously
        #to create smooth transition between frames 
        self.alight.setColor(VBase4(.8, .8, .8, 1))
        self.shiftChestUnits,self.intervals=.1,52.0
        x,y,z=self.treasureChest.getPos()
        newx=x+self.shiftChestUnits
        self.treasureChest.setPos(newx,y,z)
        self.moveCamera()
        if int(x)==self.camPosx-10:
            #if we get within a range of acceptable values
            # we set up our homepage 
            self.homePage()
            return task.done
        else:
            return task.cont
    
    def moveCamera(self):
        self.originalZ,self.targetZ=28.0,22.0
        self.shiftCameraZ=(self.originalZ-self.targetZ)/self.intervals
        self.pitchChange=25.0/self.intervals
        newPitch=self.camera.getP()+self.pitchChange
        newHeight=self.camera.getPos()[2]-self.shiftCameraZ
        camerax,cameray=self.camera.getPos()[0],self.camera.getPos()[1]
        self.camera.setPos(camerax,cameray,newHeight)
        self.camera.setP(newPitch)
        
    def generateFireFlies(self,x,y,n):
        zLowerLimit=21.0
        zHigherLimit=22.0
        light=self.fireFlyList[n]
        self.xFirefly=random.uniform(-x,x)
        self.yFirefly=random.uniform(-y,y)
        self.zFirefly=random.uniform(zLowerLimit,zHigherLimit)
        light.setPos(self.xFirefly,self.yFirefly,self.zFirefly)
        
    def setUpFog(self):
        self.fogDensity=.03
        myFog = Fog("fog")
        myFog.setColor(1,1,1)
        myFog.setExpDensity(self.fogDensity)
        render.setFog(myFog)
        
    def displayHelpPanel(self):
        self.dummyNode1=self.createDummyNode("self.dummyNode1")
        self.dummyNode2=self.createDummyNode("self.dummyNode2")
        self.dummyNode3=self.createDummyNode("self.dummyNode3")
        self.floorPlan=OnscreenImage(
            image="floorplan.png",
            scale=(.4,.25,.55),
            pos=(.7,0,.3))
        self.floorPlan.setTransparency(TransparencyAttrib.MAlpha)
        self.floorPlan.reparentTo(self.dummyNode1)
        self.displayToggleBar()
        self.displayAdjacencies()
        taskMgr.doMethodLater(.1, self.createSubTitle, 'textFadeInOut')
       
    def createSubTitle(self,task):
        self.previousTitlePos=(-1.205,.89)
        self.nextTitlePos=(-1.195,-.43)
        try:
            self.titlePrevious.destroy()
            self.titlePrevious=OnscreenText(
                text="[Previous]",pos=self.previousTitlePos,
                scale=.045,fg=(1,1,1,self.fade))
        except:
            self.titlePrevious=OnscreenText(
                text="[Previous]",pos=self.previousTitlePos,
                scale=.045,fg=(1,1,1,self.fade))
        try :
            self.titleNext.destroy()
            self.titleNext=OnscreenText(
                text="[Next]",pos=self.nextTitlePos,scale=.045,fg=(1,1,1,self.fade))
        except: 
            self.titleNext=OnscreenText(
                text="[Next]",pos=self.nextTitlePos,
                scale=.045,fg=(1,1,1,self.fade))
        return task.again
        
    def createDummyNode(self,name):
        name=render.attachNewNode("2d")
        name.reparentTo(aspect2d)
        return name 

    def displayToggleBar(self):
        self.toggleBarImage=DirectButton(
            image = "hidebar.png",scale=(.07,0.1,.55),pos=(1.17,0,.3),
            relief=None,command=lambda: self.switchDisplays(
                self.toggleBar,self.dummyNode1,self.toggleBarImage,
                "hidebar.png","showbar.png",
                (.07,0.1,.55),(1.17,0,.3)))
        self.togglePreviousBar()
        self.toggleNextBar()
    
    def togglePreviousBar(self):
        self.previousBarPos=(-1.2,0,.57)
        self.togglePreviousBarImage=(DirectButton(
        image = "hidebarshort.png",
        scale=(.07,0.1,.195),pos=self.previousBarPos,relief=None,
        command= lambda: self.switchDisplays(
            self.togglePreviousCard,
            self.dummyNode2,self.togglePreviousBarImage,
            "hidebarshort.png","showbarshort.png",
            (.07,0.1,.195),self.previousBarPos)))
            
    def toggleNextBar(self):
        self.nextBarPos=(-1.2,0,-.7)
        self.toggleNextBarImage=(DirectButton(
        image = "hidebarshort.png",
        scale=(.07,0.1,.195),pos=self.nextBarPos,relief=None,
        command= lambda: self.switchDisplays(
            self.toggleNextCard,self.dummyNode3,self.toggleNextBarImage,
            "hidebarshort.png","showbarshort.png",
            (.07,0.1,.195),self.nextBarPos)))
            
    def switchPreviousCardDisplay(self):
        self.toggleBarPrevious=not(self.toggleBarPrevious)
        
    def displayAdjacencies(self):
        if self.previousCard:
            self.displayPreviousCard()
        if self.nextCard:
            self.displayNextCard()
            
    def displayPreviousCard(self):
        self.previousCardPos=(-1,0,.58)
        self.previousCardTextPos=(-.9,.57)
        prevCard=self.previousCard.split(".")[0]
        self.previousCard=OnscreenImage(
            image=self.previousCard,pos=self.previousCardPos,
            scale=(0.07,0.82,0.12))
        self.previousCard.reparentTo(self.dummyNode2)
        try:
            self.assocPrevText.destroy() 
            self.assocPrevText=OnscreenText(
                text="(%s)"%self.inputs[prevCard],
                pos=self.previousCardTextPos,
                scale=.06,fg=(1,1,1,1),align=TextNode.ALeft)
            self.assocPrevText.reparentTo(self.dummyNode2)
        except:
            self.assocPrevText=OnscreenText(
                text="(%s)"%self.inputs[prevCard],
                pos=self.previousCardTextPos,
                scale=.06,fg=(1,1,1,1),align=TextNode.ALeft)
            self.assocPrevText.reparentTo(self.dummyNode2)
    
    def displayNextCard(self):
        self.nextCardPos=(-1,0,-.685)
        self.nextCardTextPos=(-.9,-.69)
        nextCard=self.nextCard.split(".")[0]
        self.nextCard=OnscreenImage(
            image=self.nextCard,pos=self.nextCardPos,scale=(0.07,0.82,0.12))
        self.nextCard.reparentTo(self.dummyNode3)
        try:
            self.assocNextText.destroy()
            self.assocNextText=OnscreenText(
                text="(%s)"%self.inputs[nextCard],
                pos=self.nextCardTextPos,
                scale=.06,fg=(1,1,1,1),align=TextNode.ALeft)
            self.assocNextText.reparentTo(self.dummyNode3)
        except:
            self.assocNextText=OnscreenText(
                text="(%s)"%self.inputs[nextCard],
                pos=self.nextCardTextPos,scale=.06,
                fg=(1,1,1,1),align=TextNode.ALeft)
            self.assocNextText.reparentTo(self.dummyNode3)
            
            
    def switchDisplays(self,toggleBar,dummyNode,imageNode,hideImage,
                       showImage,scale,pos):
        toggleBar=not(toggleBar)
        if toggleBar==True:
            dummyNode.show()
            imageNode.destroy()
            imageNode=(DirectButton(image = hideImage,scale=scale,pos=pos,
                                    relief=None, command=lambda:
                                        self.switchDisplays(
                                            toggleBar,dummyNode,
                                            imageNode,hideImage,
                                            showImage,scale,pos)))
        else:
            dummyNode.hide()
            imageNode.destroy()
            imageNode=(DirectButton(image = showImage,scale=scale,pos=pos,
                                    relief=None, command= lambda:
                                        self.switchDisplays(
                                            toggleBar,dummyNode,
                                            imageNode,hideImage,
                                            showImage,scale,pos)))

    def shuffleCards(self):
        self.shuffledCardNames=[]
        self.shuffledCardFaces=copy.copy(cardFaces)
        random.shuffle(self.shuffledCardFaces)
        for face in self.shuffledCardFaces:
            self.shuffledCardNames.append(face.split(".")[0])
        
    def setUpCollisionRay(self):
        #Make a collision node for ours selection ray
        #Repurposed from Panda3D Documentation
        self.selectionNode = CollisionNode('mouseRay')
        self.selectionNP = camera.attachNewNode(self.selectionNode)
        self.selectionNode.setFromCollideMask(
            GeomNode.getDefaultCollideMask())
        self.selectionNode.setFromCollideMask(1)
        self.selectionNode.setIntoCollideMask(0)
        self.selectionRay = CollisionRay()
        #Make our ray
        self.selectionNode.addSolid(self.selectionRay)
        #Add it to the collision node
        #Register the ray as something that can cause collisions
        self.cTrav.addCollider(self.selectionNP,self.queue)
    
    def setUpCollisionNode(self):
        #add a collision node to our camera
        self.fromObject = base.camera.attachNewNode(
            CollisionNode('colNode'))
        self.fromObject.setPos(0,0,3)
        self.fromObject.node().addSolid(CollisionSphere(0, 0, 0, .5))
        self.fromObject.node().setIntoCollideMask(0)
        self.cTrav.addCollider(self.fromObject,self.pusher)
        self.pusher.addCollider(
            self.fromObject, base.camera, base.drive.node())
        
    def setInputs(self):
        self.accept("mouse1",self.mouse1Tasks)
        self.accept('escape', sys.exit)

        
    def playFootSteps(self):
        self.soundSteps.play()
        
    def mouse1Tasks(self):
        self.mouseTask()
        
    def setUpScene(self):
        #self.setUpControls()
        self.setUpBackground()
        #set up the items where we can store information
        self.setUpItems()
    
    def mouseTask(self):
        self.scale=53
        self.loadItemList()
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            self.selectionRay.setFromLens(
                base.camNode, mpos.getX(), mpos.getY())
            #self.cTrav.showCollisions(render)
            if self.queue.getNumEntries() > 0:
                self.mouseEntry()
    
    def mouseEntry(self):
        #if we've clicked on something
        self.queue.sortEntries()
        #we get closest item
        pickedObj = self.queue.getEntry(0).getIntoNodePath().getTag("items")
        #check if what we clicked is what we want (has proper tag)
        if len(pickedObj)>0 and (pickedObj not in self.visitedItems):
            self.mouseTaskSupport(pickedObj)
        if self.queue.getEntry(0).getIntoNodePath().getTag("openChest"):
            self.toggleChest=True
            
    def mouseTaskSupport(self,pickedObj):
        self.assocs[
            self.shuffledCardNames[self.counter]]=self.items[int(pickedObj)]
        self.counter+=1
        self.visitedItems.append(pickedObj)
        #self.queue.getEntry(0).getIntoNodePath().clearTag("items")
        #if len(self.visitedItems)==len(self.items):
        if len(self.visitedItems)==5:
            self.testMemory()
        self.drawMiniCards(-self.camera.getPos()[1]/self.scale+.40,
                           self.camera.getPos()[0]/self.scale-.2)
        self.updateDisplayCards()
        self.displayAdjacencies()
    
    def loadItemList(self):
        self.items=["painting","post","tv","bed","carpet","table","tree",
                    "shelf","loveSeat1","loveSeat2","longSofa",
                    "dinnerTable","dinnerChair1","dinnerChair2"]
    def testMemory(self):
        self.nextButton=DirectButton(image = 'arrow.png',
                                     scale=.15,pos=(0.8,0,-0.6),
                                     relief=None, command=self.recallMemory)
        self.nextButton.setTransparency(TransparencyAttrib.MAlpha)
    
    def displayPriorityArrow(self):
        self.arrow=OnscreenImage(image="arrow2.png",
                                 scale=(.05,.1,.05),pos=(-.51,0,-.6),
                                 color=(1,0,0,0))
        self.arrow.setTransparency(TransparencyAttrib.MAlpha)
        taskMgr.doMethodLater(.1, self.fadeArrow, 'arrowFadeInOut')
    
    def displayUserLocation(self,task,scale=(.05,1,.05)):
        self.updateFade()
        if self.userLocation!=None:
            self.userLocation.destroy(),self.userAngle.destroy()
        x=-self.camera.getPos()[1]/self.scale+.40
        y=self.camera.getPos()[0]/self.scale-.2
        self.userLocation=OnscreenImage(
            image="dot.png",pos=(x,0,y),scale=scale,
            color=(1,1,1,self.fade))
        self.userAngle=OnscreenImage(
            image="rotating.png",pos=(x,0,y),scale=scale,
            color=(1,1,1,self.fade))
        self.userAngle.setR(-self.camera.getHpr()[0])
        self.userLocation.setTransparency(TransparencyAttrib.MAlpha)
        self.userAngle.setTransparency(TransparencyAttrib.MAlpha)
        self.userLocation.reparentTo(self.dummyNode1)
        self.userAngle.reparentTo(self.dummyNode1)
        return Task.again
    
    def updateFade(self):
        if self.fadeToggle==True:
            self.fade+=.05
            if self.fade>1:
                self.fadeToggle=False
        elif self.fadeToggle==False:
            self.fade-=.05
            if self.fade<0:
                self.fadeToggle=True
        
    def drawMiniCards(self,x,y):
        self.lastCoord+=([[x,0,y]])
        self._draw_line_segs(self.dummyNode1,self.lastCoord)
        for i in xrange(len(self.lastCoord)):   
            self.miniCards=OnscreenImage(
                image=self.shuffledCardFaces[i],
                pos=(self.lastCoord[i][0],0,self.lastCoord[i][2]),
                scale=(0.03,0.82,0.050))
            self.miniCards.reparentTo(self.dummyNode1)
        
    def _draw_line_segs(self, parent, points, thickness=1.5):
        segs = LineSegs()
        segs.setThickness(thickness)
        segs.setColor( Vec4(1,0,0,.35) )
        if points:
            segs.moveTo(points[0][0], points[0][1], points[0][2])
            for p in points[1:]:
                segs.drawTo(p[0], p[1], p[2])
        lines = NodePath(segs.create())
        lines.reparentTo(parent)

    def recallMemory(self):
        self.checkList=[]
        self.checkListFaces=[]
        self.startCard=0
        self.endCard=13
        self.cardSet=0
        self.bk=OnscreenImage(image="bk.png",scale=(2,1,1))
        self.recallCards(self.startCard,self.endCard, self.cardSet,0)
        self.scaleCards=(0.1,0.1,0.13)
        scaleCards2=(0.07,0.05,0.10)
        self.recallMemoryPrompt=OnscreenText(
                    text="List the cards in the sequence as you recall",
                    pos=(0,.45),scale=.045,fg=(0,0,0,.75))

    def recallCards(self,startCard,endCard,cardSet,createEntries=1):
        for i in xrange(startCard,endCard):
            x=2*(i+1)/(self.numCards+1.0)-1-cardSet*1.75
            self.cardsPos.append(x)
            self.createButtons(i,x)
            if createEntries==1:
                self.createEntries(x, cardSet)
        for image in self.buttonList:
            image.setTransparency(TransparencyAttrib.MAlpha)
    
    def createButtons(self,i,x):
        self.buttonList.append(DirectButton(
            image = cardFaces[i],scale=(0.06,0.1,0.095),pos=(x,0,.3),
            relief=None, command=lambda: self.createCheckButtons(i)))
        
    def createCheckButtons(self,i):
        self.correctCount=0
        self.checkList.append(i)
        self.checkListFaces.append(cardFaces[i])
        for i in xrange(len(self.checkList)):
            x=2*(i+1)/(self.numCards+1.0)-1
            self.cards=OnscreenImage(image=self.checkListFaces[i],
                                     pos=(x,0,-.2),scale=(0.06,0.1,0.095))
        if len(self.checkList)==13:
            correct=self.testResults()
            self.results=OnscreenText(
                text="You recalled %d out of %d correctly"%(
                    correct,self.numCards),pos=(0,-0.85),scale=.1)
    
    def testResults(self):
        for i in xrange(len(self.shuffledCardFaces)):
            if self.shuffledCardFaces[i]==self.checkListFaces[i]:
                self.correctCount+=1
        return self.correctCount 
            
    def updateDisplayCards(self):
        self.numCardsCopy-=1
        self.previousCard=self.shuffledCardFacesCopy.pop(0)
        if len(self.shuffledCardFacesCopy)!=0:
            self.nextCard=self.shuffledCardFacesCopy[0]
        else: self.nextCard=False 
        for image in self.imageList:
            image.destroy()
        self.displayCards()
        
    def displayCards(self):
        for i in xrange(self.numCardsCopy):
            x=2*(i+1)/(self.numCards+1.0)-.65
            self.cardsPos.append(x)
            self.imageList.append(OnscreenImage(
                image="%s"%(self.shuffledCardFacesCopy[i]),
                pos=(x,0,-.8),scale=(0.05,0.05,0.08)))
            #we use middle numbers as coordinates
    def fadeArrow(self,task): 
        self.arrow.setColor(1,0,0,self.fade) 
        return task.cont
        
    def setUpBackground(self):
        self.scale=10
        #load grass and set position, scale, and texture
        self.walls=loader.loadModel("Walls")
        self.walls.setPos(0,0,0)
        self.walls.setScale(self.scale,self.scale,self.scale)
        walltex1 = loader.loadTexture('walltex1.png')
        self.walls.setTexture(walltex1)
        #render our object
        self.walls.reparentTo(render)
        self.loadColGeomsSet1()
        self.loadColGeomsSet2()
        self.setUpBackgroundSupport()
    
    def setUpBackgroundSupport(self):
        for geom in self.colGeoms:
            self.createCollisionGeom(*geom)
        cFloorNode=CollisionNode('floorCollision')
        floorQuad=CollisionPolygon(Point3(5, 0, 0), Point3(-1.5,0,0),
                                   Point3(-1.5, -4, 0),Point3(5, -4, 0))
        cFloorNode.addSolid(floorQuad)
    
    def loadColGeomsSet1(self):
        self.colGeoms=[
            (11,(2.4,-1.80,1),(2.4,-1.80,0),(.55,-1.80,0),
            (.55,-1.80,1)),#Interior 2b (firsthalf),
            (1,(5,-.05,0),(5,-.05,1),(-1.5,-.05,1), (-1.5,-.05,0)),#West Wall
            (2,(-1.5,0,0),(-1.5,0,1),(-1.5,-4,1), (-1.5,-4,0)),#South Edge
            (5,(0.52,0,0),(0.52,0,1),(0.52,-1.2,1), (0.52,-1.2,0)),
            #South Wall_1_Interior
            (3,(0.38,0,1),(0.38,0,0),(0.38,-1.2,0), (0.38,-1.2,1)),
            #South Wall_1_Exterior
            (4,(0.38,-1.7,1),(0.38,-1.7,0),(0.38,-4,0),(0.38,-4,1)),
            #South Wall_2_Exterior
            (6,(0.52,-1.7,0),(0.52,-1.7,1),(0.52,-4,1),(0.52,-4,0)),
            #South Wall_2 Interior
            (7,(1.8,0,1),(1.8,0,0),(1.8,-1.45,0),(1.8,-1.45,1)),
            #Interior 1 (TV)
            (8,(1.9,0,0),(1.9,0,1),(1.9,-1.45,1),(1.9,-1.45,0)),
            #Interior 1b (TV)
            (9,(2.4,-1.95,0),(2.4,-1.95,1),(.55,-1.95,1), (.55,-1.95,0)),
            #Interior 2 (firsthalf)
            (10,(3.95,-1.95,0),(3.95,-1.95,1), (2.7,-1.95,1),(2.7,-1.95,0))]
            #Interior 2 (secondhalf)
        
    def loadColGeomsSet2(self):
        self.colGeoms+=[
            (12,(3.95,-1.80,1),(3.95,-1.80,0), (2.7,-1.80,0),
              (2.7,-1.80,1)), #Interior 2b (secondhalf)
            (13,(2.95,-1.9,0),(2.95,-1.9,1),(2.95,-2.1,1),
                (2.95,-2.1,0)),#North Wall 1 Exterior (firsthalf)E
            (14,(2.95,-2.48,0),(2.95,-2.48,1),(2.95,-4,1),
                (2.95,-4,0)),#North Wall 1 Exterior (secondhalf)E
            (15,(2.7,-1.9,1),(2.7,-1.9,0),(2.7,-2.1,0),
                (2.7,-2.1,1)), #North Wall 1b Interior (firsthalf) E
            (16,(2.7,-2.48,1),(2.7,-2.48,0),(2.7,-4,0),
                (2.7,-4,1)), #North Wall 1b Interior (secondhalf) E
            (17,(3.82,0,1),(3.82,0,0),(3.82,-.35,0),
                Point3(3.82,-.35,1)),#North Wall 2 Interior (firsthalf) W
            (18,(3.82,-1.1,1),(3.82,-1.1,0),(3.82,-1.9,0),
                Point3(3.82,-1.9,1)),#North Wall 2 Interior (secondhalf) W
            (19,(4,0,0),(4,0,1),(4,-.35,1),
                Point3(4,-.35,0)),#North Wall 2 Exterior (firsthalf) W
            (20,(4,-1.1,0),(4,-1.1,1),(4,-1.9,1),
                Point3(4,-1.9,0))#North Wall 2 Exterior (secondhalf) W
            ]
        
    def createCollisionGeom(self,n,firstPts,secondPts,thirdPts,fourthPts):
        collisionNode="wallCollision%d"%n
        collisionNodeName="cWallNode%d"%n
        collisionNodeName=CollisionNode(collisionNode)
        quadName="wallQuad%d"%n
        quadName=CollisionPolygon(Point3(firstPts),Point3(secondPts),
                                  Point3(thirdPts),Point3(fourthPts))
        collisionNodeName.addSolid(quadName)
        self.wallC=self.walls.attachNewNode(collisionNodeName)
        
        self.roof=self.loadItems("Roof","rooftex.png",scaleX=6,scaleY=6)
        self.walls2=self.loadItems("Walls2","walltex2.png")
        self.grass=self.loadItems("grass",'8CYNDAC0.png')
        self.floor=self.loadItems("floor","floor.png")
        self.exterior=self.loadItems("exterior",'brick.png')
        
    def setUpItems(self):
        self.itemList=[]
        self.scale=10
        self.tv=self.loadItems("tv",'tv.png')
        self.carpet=self.loadItems("carpet","carpet.png")
        self.white=self.loadItems("white","walltex2.png",8,4)
        self.painting=self.loadItems("painting","kosbie.png")
        self.wood=self.loadItems("wood","wood.png",8,4)
        self.tree=self.loadItems("GroomedTree",None,1,1,.9,(52,-5,0))
        self.shelf=self.loadItems("shelf","darkwood.png")
        self.couches=self.loadItems("couch","leather.png",5,5)
        self.dining=self.loadItems("chairs","wood.png")
        self.treasureChest=self.loadItems(
            "treasurechest","woodpanel.png",1,1,None,(0,0,20))
        self.sky=self.loadItems("sky","sky.png",1,1)
        self.selectionItems = render.attachNewNode("selectionRoot")
        self.setUpCollisionGeom()
        
    def setUpCollisionGeom(self):
        self.paintingNode=self.loadCollisionPolygon(
            "painting",self.painting,(3.35,-.07,.45),(3.35,-.07,.8),
            (2.9,-.07,.8),(2.9,-.07,.45))
        self.postNode=self.loadCollisionTube(
            "post",self.wood,.25,-2,0,.25,-2,.55,.03)
        self.tvNode=self.loadCollisionPolygon(
            "tv",self.tv,(1.75,-.35,.78),(1.75,-.35,.5),(1.75,-1.1,.5),
            (1.75,-1.1,.78))
        self.bedNode=self.loadCollisionPolygon(
            "bed",self.white,(1,-2.7,.17),(.5,-2.7,.17),(.5,-1.9,.17),
            (1,-1.9,.17))
        self.carpetNode=self.loadCollisionPolygon(
            "carpet",self.carpet,(1.95,-3.15,.05),(2.4,-3.15,.05),
            (2.4,-2.55,.05),(1.95,-2.55,.05))
        self.tableNode=self.loadCollisionPolygon(
            "table",self.wood,(1,-3.5,.26),(1.45,-3.5,.26),
            (1.45,-3.1,.26),(1,-3.1,.26))
        self.supportSetUpCollisionGeom()
        
    def supportSetUpCollisionGeom(self):
        self.treeNode=self.loadCollisionTube(
            "tree",self.tree,0,0,0,0,0,7,2)
        self.shelfNode=self.loadCollisionPolygon(
            "shelf",self.shelf,(.6,-0.05,.78),(.6,-0.05,0),
            (.6,-.43,0),(.6,-.43,.78))
        self.couchNode1=self.loadCollisionTube(
            "couch1",self.couches,1.05,-.96,0,1.05,-.96,.2,.2)
        self.couchNode2=self.loadCollisionTube(
            "couch2",self.couches,1.45,-.96,0,1.45,-.96,.2,.2)
        self.couchNode3=self.loadCollisionTube(
            "couch3",self.couches,1.00,-.16,.1,1.5,-.16,.1,.2)
        self.dinnerTable=self.loadCollisionPolygon(
            "dinnerTable",self.dining,(3.6,-.89,.26),(3.6,-.61,.26),
            (3.1,-.61,.26),(3.1,-.89,.26))
        self.dinnerChairNode1=self.loadCollisionTube(
            "dinnerChair1",self.dining,2.9,-.75,0,2.9,-.75,.2,.1)
        self.dinnerChairNode2=self.loadCollisionTube(
            "dinnerChair1",self.dining,3.7,-.75,0,3.7,-.75,.2,.1)
        self.chestNode=self.loadCollisionTube(
            "chest",self.treasureChest,.02,.02,.25,.07,.07,.25,.25)
        self.chestNode.setTag(
            "openChest","1")
        
        self.itemList+=(self.paintingNode,self.postNode,self.tvNode,
                        self.bedNode,self.carpetNode,self.tableNode,
                        self.treeNode,self.shelfNode,self.couchNode1,
                        self.couchNode2,self.couchNode3,self.dinnerTable,
                        self.dinnerChairNode1,self.dinnerChairNode2)
        self.setTag(self.itemList,"items")
        
    def setTag(self):
        self.itemList+=(self.paintingNode,self.postNode,self.tvNode,
                        self.bedNode,self.carpetNode,self.tableNode,
                        self.treeNode,self.shelfNode,
                        self.couchNode1,self.couchNode2,self.couchNode3,
                        self.dinnerTable,self.dinnerChairNode1,
                        self.dinnerChairNode2)
        self.setTag(self.itemList,"items")
        
    def setTag(self,node,tagKey):
        for i in xrange(len(node)):
            node[i].setTag(tagKey,str(i))
        
    def loadItems(self,modelName,texture=None,scaleX=1,scaleY=1,
                  scale=None,pos=(0,0,0)):
        if scale==None: scale=self.scale
        modelName=loader.loadModel(modelName)
        modelName.setPos(pos)
        modelName.setScale(scale,scale,scale)
        ts=TextureStage("ts")
        if texture!=None:
            modelTex=loader.loadTexture(texture)
            modelName.setTexture(ts,modelTex)
            modelName.setTexScale(ts,scaleX,scaleY)
        modelName.reparentTo(render)
        return modelName
    
    def loadCollisionPolygon(self,modelName,attachGeom,firstPts,
                             secondPts,thirdPts,fourthPts):
        modelName=CollisionNode(modelName)
        quadName=CollisionPolygon(Point3(firstPts),Point3(secondPts),
                                  Point3(thirdPts),Point3(fourthPts))
        modelName.addSolid(quadName)
        modelName=attachGeom.attachNewNode(modelName)
        return modelName
    
    def loadCollisionTube(self,modelName,attachGeom,x0,y0,z0,x1,y1,z1,
                          radius):
        modelName=CollisionNode(modelName)
        cylinder=CollisionTube(x0,y0,z0,x1,y1,z1,radius)
        modelName.addSolid(cylinder)
        modelName=attachGeom.attachNewNode(modelName)
        return modelName
    
    def homePage(self):
        self.introduction=False 
        #self.setUphomePageSFX()
        self.introButton=DirectButton(
            image=("introduction.png"),scale=.5,pos=(-0.8,0,-0.65),
            relief=None,command=self.startIntro)
        self.introButton.setTransparency(TransparencyAttrib.MAlpha)
        self.startButton=DirectButton(
            image=("beginJourney.png"),scale=.5,pos=(+0.8,0,-0.65),
            relief=None, command=self.startJourney)
        self.startButton.setTransparency(TransparencyAttrib.MAlpha)
        self.cylinder=self.loadItems(
            "cylinder","wood.png",1,1,2,(9,-1.3,20.8))
        self.hexagon=self.loadItems(
            "hexagon","wood.png",1,1,2.5,(9,1.4,20.8))
        taskMgr.add(self.rotateMenuItems, 'rotateMenuItems')
    
    #def setUphomePageSFX(self):
        #self.volume=0
        #self.circusInTheSky.setVolume(0)
        #self.circusInTheSky.setLoop(1) 
        #self.circusInTheSky.play()
        #taskMgr.doMethodLater(.5, self.playCircusInTheSky,
        #                      'Fade in Music', extraArgs = [self])
        
    #def playCircusInTheSky(self,task):
        #self.volume+=.00125
        #self.circusInTheSky.setVolume(self.volume)
        #return Task.cont
            
    def rotateMenuItems(self,task):
        self.speed=1.5
        radius=.5
        angle = radians(self.heading)
        x = cos(angle) * radius
        y = sin(angle) * radius
        z = sin(angle) * radius
        self.heading+=self.speed
        self.heading%=360
        self.cylinder.setH(self.heading)
        self.hexagon.setH(self.heading)
        if self.introduction==True:
            self.cylinder.remove()
            self.hexagon.remove()
            return task.done 
        return Task.cont

    def startJourney(self):
        #self.circusInTheSky.stop()
        self.introButton.destroy()
        self.startButton.destroy()
        self.initSetUpAssoc()
        #self.setUp3DEnvironmentIntro()
        ###########change here 
        
    def setUp3DEnvironmentIntro(self):
        self.camera.setP(25)
        self.Enviro3DDummy=self.createDummyNode("3DEnviroDummy")
        self.textBlocks,self.color,self.keyBrightenComplete=[],0.01,False
        self.displayCards()
        self.displayHelpPanel()
        taskMgr.doMethodLater(.05,self.displayUserLocation, 'Track User',
                              extraArgs = [self])
        self.setUpDirectionalLight()
        self.displayPriorityArrow()
        self.accept("arrow_down",self.playFootSteps)
        self.accept("arrow_up",self.playFootSteps)
        self.enviroTextBlocks()
        self.Enviro3DSupportText()
    
    def enviroTextBlocks(self):
        self.enviroTextBlock1=(
            "1. Here is the priority queue for the shuffled cards")
        self.enviroTextBlock2=(
            "2. Toggle displays to show/hide windows")
        self.enviroTextBlock3=(
            "3. See your location in the plan")
        self.textBlocks+=(self.enviroTextBlock1,self.enviroTextBlock2,
                               self.enviroTextBlock3)
        self.textPos=[(0,-.6),(-.6,.6),(.7,-.4)]
        
    def Enviro3DSupportText(self):
        for i in xrange(len(self.textBlocks)):
            self.titleText=OnscreenText(text=self.textBlocks[i],
            pos=self.textPos[i],scale=.058,fg=(1,1,1,1))
            self.titleText.reparentTo(self.Enviro3DDummy)
        taskMgr.doMethodLater(.1, self.init3DActiveEnviro,'3DEnviroEntry')
        taskMgr.doMethodLater(.15,self.brightenKey,"brightenKey")
    
    def init3DActiveEnviro(self,task):
        self.keyButton=DirectButton(
            image = 'key.png',scale=(.5,.2,.15),color=(0,0,0,0),pos=(-.5,0,0),
            relief=None, command=self.setUp3DEnvironmentActive)
        self.keyButton.setTransparency(TransparencyAttrib.MAlpha)
        self.keyButton.reparentTo(self.Enviro3DDummy)
        self.keyButton['state'] = DGG.DISABLED
        return task.done 
        
    def brightenKey(self,task):
        if self.keyBrightenComplete==False:
            self.brightenSpeed=0.025
            if self.color<1:
                self.color+=self.brightenSpeed
                self.keyButton.setColor(0,0,0,self.color)
                return task.again
            else:
                self.entryText=OnscreenText(text="[Click the key to begin]",
                pos=(-.7,.13),scale=.058,fg=(1,1,1,1))
                self.entryText.reparentTo(self.Enviro3DDummy)
                self.keyButton['state'] = DGG.NORMAL
                task.done
        else:
            task.done 

    def setUp3DEnvironmentActive(self):
        base.useDrive()
        self.keyBrightenComplete=True 
        self.Enviro3DDummy.removeNode()

    def setUpDirectionalLight(self):
        dlight = DirectionalLight('dlight')
        dlight.setColor(VBase4(0.8, 0.8, 0.5, 1))
        dlnp = render.attachNewNode(dlight)
        dlnp.setHpr(0, -60, 0)
        render.setLight(dlnp)
        render.setShaderAuto()
        
    def startIntro(self):
        self.introduction=True 
        self.introButton.destroy()
        self.startButton.destroy()
        self.setUpHelp()

    def setUpHelp(self):
        self.titleText=OnscreenText(text="Introduction",
                                    pos=(-0.85,0.85),scale=.1)
        self.text = TextNode('helpText')
        self.textBlocks()
        self.text.setText(self.textBlock1)
        textNodePath = aspect2d.attachNewNode(self.text)
        textNodePath.setScale(0.07)
        textNodePath.setPos(-1,0,0)
        self.text.setWordwrap(30.0)
        self.nextButton=DirectButton(
            image = 'arrow.png',scale=.15,pos=(0.8,0,-0.6),relief=None,
            command=self.nextPage )
        self.nextButton.setTransparency(TransparencyAttrib.MAlpha)
    
    def textBlocks(self):
        self.textBlock1=("This project tests the effectiveness"
        +" of along established 'Method of loci', which is a"
        +" mnemonic device used for memory enhancement which uses"
        +" visualization to organize and recall information."
        +" We will be using this technique to memory a set of 13"
        +" cards (one suit)")
        
        self.textBlock2=(
        "STEP 1 \n\n We create rooms which are connected "
        + "and unique. These are provided for you."
        +"\n\n STEP 2 \n\n Associate each card with visual "
        +"objects (eg. 2 ---> Swan)"
        +"\n\n STEP 3 \n\n We 'place' the cards at specific "
        +"locations in sequence so relationship between "
        +"the location and item are made."
        +"\n\n STEP 4 \n\n Test the associations we've made")
        
    def nextPage(self):

        textNodePath = aspect2d.attachNewNode(self.text)
        textNodePath.setPos(-1,0,.5)
        self.nextButton.destroy()
        self.text.setText(self.textBlock2)
        self.nextButton=DirectButton(
            image = 'arrow.png',scale=.15,pos=(0.8,0,-0.6),relief=None,
            command=(self.clear))
        self.nextButton.setTransparency(TransparencyAttrib.MAlpha)
        
    def clear(self):
        self.text.clearText()
        self.titleText.clearText()
        self.nextButton.destroy()
        self.homePage()
        
    def initSetUpAssoc(self):
        self.bk=OnscreenImage(image="bk.png",scale=(2,1,1))
        self.inputs=dict()
        self.cardsPositions=[]
        self.imageListFaces,self.textObjs,self.entries=[],[],[]
        self.numCardsPage1=7
        self.startCard=0
        self.endCard=7
        self.cardSet=0
        self.callCards(self.startCard,self.endCard, self.cardSet)
        self.goAhead=[]
        self.button1=loader.loadMusic("button1.wav")
        self.assocTextBlocks()
        taskMgr.doMethodLater(.1, lambda task: self.createAssocHelperText(
            task,self.assocTextBlock1),'assocHelperText')
        
    def assocTextBlocks(self):
        self.assocTextBlock1=(
            "[Enter a word you strongly associated with each card]"
            +"\n Helpful Hint: Use less abstract and more descriptive words")
        self.assocTextBlock2=(
            "[That's great! Finish up the rest!]")
            
    def createAssocHelperText(self,task,text):
        self.updateFade()
        try:
            self.assocText.destroy()
            self.assocText=OnscreenText(
            text=text,
            pos=(0,-.2),scale=.05,fg=(0,0,0,self.fade))
        except:
            self.assocText=OnscreenText(
            text=text,
            pos=(0,-.2),scale=.05,fg=(0,0,0,self.fade))
        return task.again 
            
    def callCards(self,startCard,endCard,cardSet,createEntries=1,
                  scaleCards=(0.1,0.1,0.13)):
        for i in xrange(startCard,endCard):
            x=2*(i+1)/(self.numCardsPage1+1.0)-1-cardSet*1.75
            self.cardsPositions.append(x)
            self.imageListFaces.append(
                OnscreenImage(image="%s"%(cardFaces[i]),
                              pos=(x,0,.3),scale=scaleCards))
            self.textObjs.append(OnscreenText(text=str(i),pos=(x,0)))
            #we use middle numbers as coordinates
            self.cardName=cardNames[i]
            if createEntries==1:
                self.createEntries(x, cardSet)
            
    def createEntries(self,x, cardSet):
        self.entries.append(
            DirectEntry(text = "" ,scale=.02,pos=(x-0.1,0.1,0.1),
                        command=(lambda textEntered: self.storeAssoc
                                 (textEntered, x, cardSet)), numLines = 2))
    
    def clearPage(self):
        for image in self.imageListFaces:
            image.destroy()
        for textObj in self.textObjs:
            textObj.destroy()
        for entry in self.entries:
            entry.destroy()
        for image in self.goAhead:
            image.destroy()
        self.assocText.destroy()
        self.clearBK()

            
    def clearBK(self):
        self.bk.destroy()
    
    def storeAssoc(self,textEntered, x, cardSet):
        index=int((x+cardSet*1.75+.75)/0.25)
        self.inputs[cardNames[index]]=textEntered
        self.greenDot=OnscreenImage(
            image="greenDot.png",pos=(x,0,.55),scale=(.25,1,.25))
        self.greenDot.setTransparency(TransparencyAttrib.MAlpha)
        self.goAhead.append(self.greenDot)
        self.button1.play()
        if len(self.inputs)>6 and cardSet==0:
            taskMgr.remove('assocHelperText')
            taskMgr.doMethodLater(.1, lambda task: self.createAssocHelperText(
            task,self.assocTextBlock2),'assocHelperText')
            self.startCard=7
            self.endCard=13
            self.clearBK()
            self.cardSet=1
            self.bk=OnscreenImage(image="bk.png",scale=(2,1,1))
            self.callCards(self.startCard,self.endCard, self.cardSet)
        if len(self.inputs)>12 and cardSet==1:
            taskMgr.remove('assocHelperText')
            self.clearPage()
            self.setUp3DEnvironmentIntro()
    def startGame(self):
        self.bk.destroy()
        
w=MyApp()
run()
