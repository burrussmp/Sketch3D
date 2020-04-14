using UnityEngine;
using System.Collections;
using UnityEngine.UI;
using System.IO;
using UnityEngine.Networking;
using System;
using System.Text;
public class Buttons : MonoBehaviour
{
    private bool detected;
    public int selGridInt;
    public bool sideCaptured;
    public bool frontCaptured;
    public int widthTarget;
    public int heightTarget;
    public int bboxX;
    public int bboxY;
    public bool isError = false;
    public string mError = "";
    public float rotX,rotY,rotZ = 0.0f;
    void OnGUI()
    {
        GUIStyle currentStyleSideButton = InitStyles(sideCaptured);
        GUIStyle currentStyleTopButton = InitStyles(frontCaptured);
        GameObject parent = GameObject.Find("newObject");
        detected = parent.transform.childCount != 0;
        if (isError){
            int Xcenter = Screen.width/2;
            int Ycenter = Screen.height/2;
            widthTarget = Convert.ToInt32(0.7*Convert.ToSingle(Screen.width));
            heightTarget = Convert.ToInt32(0.4*Convert.ToSingle(Screen.height));
            bboxX = Convert.ToInt32(Xcenter - 0.5*widthTarget);
            bboxY = Convert.ToInt32(Ycenter - 0.5*heightTarget);
            Texture2D currentStyle = MakeTex( 2, 2, new Color( 1f, 0f, 0f, 1f ));
            GUI.DrawTexture(new Rect(bboxX,bboxY,widthTarget,heightTarget),currentStyle);
            GUIStyle labelStyle = new GUIStyle( GUI.skin.box );
            labelStyle.fontSize = 50;
            labelStyle.alignment = TextAnchor.MiddleCenter;
            GUI.Label(new Rect(bboxX, bboxY, widthTarget, heightTarget), mError,labelStyle);

        } else if (detected){
            string[] selStrings = new string[] {"Translate", "Scale", "Rotate"};
            // use 2 elements in the horizontal direction
            selGridInt = GUI.SelectionGrid(new Rect(10, 10, Screen.width, Screen.height/40), selGridInt, selStrings, 3);
            int x = 10;
            int y = Screen.height/40+20;
            int padding = Screen.height/40;
            int height = Screen.height/20;
            int width = Screen.width/5;
            float changeScale = 0.01f;
            if (GUI.Button(new Rect(x,y,width,height),"-X Axis")){
                if (selGridInt == 0){
                    Translate(1,-0.01f);
                } else if (selGridInt == 1){
                    Scale(1,-0.05f);
                } else if (selGridInt == 2){
                    Rotate(1,-15f);
                }
            }
            if (GUI.Button(new Rect(x+width+padding,y,width,height),"+X Axis")){
                if (selGridInt == 0){
                    Translate(1,0.01f);
                } else if (selGridInt == 1){
                    Scale(1,0.05f);
                } else if (selGridInt == 2){
                    Rotate(1,15f);
                }
            }
            if (GUI.Button(new Rect(x,y+height+padding,width,height),"-Y Axis")){
                if (selGridInt == 0){
                    Translate(2,-0.01f);
                } else if (selGridInt == 1){
                    Scale(2,-0.05f);
                } else if (selGridInt == 2){
                    Rotate(2,-15f);
                }
            }
            if (GUI.Button(new Rect(x+width+padding,y+height+padding,width,height),"+Y Axis")){
                if (selGridInt == 0){
                    Translate(2,0.01f);
                } else if (selGridInt == 1){
                    Scale(2,0.05f);
                } else if (selGridInt == 2){
                    Rotate(2,15f);
                }
            }
            if (GUI.Button(new Rect(x,y+2*height+2*padding,width,height),"-Z Axis")){
                if (selGridInt == 0){
                    Translate(3,-0.01f);
                } else if (selGridInt == 1){
                    Scale(3,-0.05f);
                } else if (selGridInt == 2){
                    Rotate(3,-15f);
                }
            }
            if (GUI.Button(new Rect(x+width+padding,y+2*height+2*padding,width,height),"+Z Axis")){
                if (selGridInt == 0){
                    Translate(3,0.01f);
                } else if (selGridInt == 1){
                    Scale(3,0.05f);
                } else if (selGridInt == 2){
                    Rotate(3,15f);
                }
            }
            // add ability to scale whole thing
            if (selGridInt == 1){
                if (GUI.Button(new Rect(x,y+3*height+3*padding,width,height),"Down")){
                    scaleWhole(-0.05f);
                }
                if (GUI.Button(new Rect(x+width+padding,y+3*height+3*padding,width,height),"Up")){
                    scaleWhole(0.05f);
                }
            }
        } else {
            //string[] selStrings = new string[] {"Capture Side Photo", "Capture Front Photo"};
            // use 2 elements in the horizontal direction
            // selGridInt = GUI.SelectionGrid(new Rect(10, 10, Screen.width, Screen.height/40), selGridInt, selStrings, 2);
            int widthOfButton = Screen.width/4;
            int x1 = Convert.ToInt32(Screen.width/4 - 0.5*widthOfButton);
            int x2 = Convert.ToInt32(3*Screen.width/4 - 0.5*widthOfButton);
            int y = Screen.height/20;
            int height = Screen.height/25;
            
            int Xcenter = Screen.width/2;
            int Ycenter = Screen.height/2;
            widthTarget = Convert.ToInt32(0.7*Convert.ToSingle(Screen.width));
            heightTarget = Convert.ToInt32(0.4*Convert.ToSingle(Screen.height));
            bboxX = Convert.ToInt32(Xcenter - 0.5*widthTarget);
            bboxY = Convert.ToInt32(Ycenter - 0.5*heightTarget);
            Texture2D currentStyle = MakeTex( 2, 2, new Color( 1f, 1f, 1f, 0.1f ));
            GUI.DrawTexture(new Rect(bboxX,bboxY,widthTarget,heightTarget),currentStyle);
            if (GUI.Button(new Rect(x1,y,widthOfButton,height),"Capture Side Photo",currentStyleSideButton)){
                StartCoroutine(TakePhoto("Side"));
            }
            if (GUI.Button(new Rect(x2,y,widthOfButton,height),"Capture Front Photo",currentStyleTopButton)){
                StartCoroutine(TakePhoto("Front"));
            }
        }
    }

    public void showError(string error){
        isError = true;
        mError = error;
    }
    public void clearError(){
        isError = false;
    }
    private Texture2D MakeTex( int width, int height, Color col )
    {
        Color[] pix = new Color[width * height];
        for( int i = 0; i < pix.Length; ++i )
        {
            pix[ i ] = col;
        }
        Texture2D result = new Texture2D( width, height );
        result.SetPixels( pix );
        result.Apply();
        return result;
    }
    private GUIStyle InitStyles(bool captured)
    {
            GUIStyle currentStyle = new GUIStyle( GUI.skin.box );
            currentStyle.fontSize = 24;
            currentStyle.alignment = TextAnchor.MiddleCenter;
            if (captured){
                currentStyle.normal.background = MakeTex( 2, 2, new Color( 0f, 0.3f, 0f, 0.5f ) );
                return currentStyle;
            } else {
                currentStyle.normal.background = MakeTex( 2, 2, new Color( 0.6f, 0.0f, 0f, 0.5f ) );
                return currentStyle;          
            }
        
    }

    IEnumerator TakePhoto(string type)  // Start this Coroutine on some button click
    {
    // NOTE - you almost certainly have to do this here:

     yield return new WaitForEndOfFrame(); 
    // it's a rare case where the Unity doco is pretty clear,
    // http://docs.unity3d.com/ScriptReference/WaitForEndOfFrame.html
    // be sure to scroll down to the SECOND long example on that doco page 

        Texture2D tex = new Texture2D(Screen.width, Screen.height,TextureFormat.RGB24, false);
        tex.ReadPixels(new Rect(0, 0, Screen.width, Screen.height), 0, 0);
        tex.Apply();

        //Encode to a PNG
        byte[] bytes = tex.EncodeToPNG();
        //string converted = Encoding.UTF8.GetString(bytes, 0, bytes.Length);
        //Write out the PNG. Of course you have to substitute your_path for something sensible
        WWWForm form = new WWWForm();
        //form.AddField("frameCount", Time.frameCount.ToString());
        // form.AddField("Width",Screen.width);
        form.AddField("Type",type);
        form.AddField("x",bboxX);
        form.AddField("y",bboxY);
        form.AddField("width",widthTarget);
        form.AddField("height",heightTarget);
        form.AddBinaryData("file", bytes);
        print("sending picture");
        // Upload to a cgi script
        var w = UnityWebRequest.Post("http://10.0.0.118:8080", form);
        yield return w.SendWebRequest();
        if (w.isNetworkError || w.isHttpError)
            print(w.error);
        else {
            string response = w.downloadHandler.text;
            if (response[0] == '1'){
                sideCaptured = true;
            }
            if (response[1] == '1'){
                frontCaptured = true;
            }
        }
        yield return null;
        // send to server
    }

    void Translate(int input,float change){
        GameObject parent = GameObject.Find("newObject");
        Vector3 parent_pos = parent.transform.position;
        if (input == 1){
            parent_pos.x = parent_pos.x + change;
            parent.transform.position = parent_pos;
        } else if (input == 2){
            parent_pos.y = parent_pos.y + change;
            parent.transform.position = parent_pos;
        } else {
            parent_pos.z = parent_pos.z + change;
            parent.transform.position = parent_pos;
        }
    }

    void Scale(int input,float change){
        GameObject parent = GameObject.Find("newObject");
        Vector3 parent_scale = parent.transform.localScale;
        if (input == 1){
            parent_scale.x = parent_scale.x + change;
            parent.transform.localScale = parent_scale;
        } else if (input == 2){
            parent_scale.y = parent_scale.y + change;
            parent.transform.localScale = parent_scale;
        } else {
            parent_scale.z = parent_scale.z + change;
            parent.transform.localScale = parent_scale;
        }
    }
    void scaleWhole(float change){
        GameObject parent = GameObject.Find("newObject");
        Vector3 parent_scale = parent.transform.localScale;
        parent_scale.x = parent_scale.x + change;
        parent_scale.y = parent_scale.y + change;
        parent_scale.z = parent_scale.z + change;
        parent.transform.localScale = parent_scale;
    }
    void Rotate(int input,float change){
        GameObject parent = GameObject.Find("newObject");
        Quaternion parent_rotate = parent.transform.rotation;
        if (input == 1){            
            rotX = (rotX + change)%360;
            
        } else if (input == 2){
            rotY = (rotY + change)%360;
        } else {
            rotZ = (rotZ + change)%360;
        }
        parent.transform.rotation = Quaternion.Euler(rotX, rotY, rotZ);
    }

}
