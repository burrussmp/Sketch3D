using System.IO;
using UnityEngine;
using UnityEngine.Networking;
using System.Collections;
using UnityEngine.UI;

public class WebCam : MonoBehaviour 
{
    // WebCamTexture webCamTexture;
    private bool detected;
    // public int selGridInt;
    void OnGUI()
    {
        GameObject parent = GameObject.Find("newObject");
        detected = parent.transform.childCount != 0;
        Debug.Log("In Webcam");
        Debug.Log(detected);
        if (!detected){
            string[] selStrings = new string[] {"Capture Side Photo", "Capture Front Photo"};
            // use 2 elements in the horizontal direction
            // selGridInt = GUI.SelectionGrid(new Rect(10, 10, Screen.width, Screen.height/40), selGridInt, selStrings, 2);
            int x = 10;
            int y = Screen.height/40+20;
            int padding = Screen.height/40;
            int height = Screen.height/20;
            int width = Screen.width/5;
            if (GUI.Button(new Rect(x,y,width,height),"Capture Side Photo")){
                StartCoroutine(TakePhoto());
            }
            if (GUI.Button(new Rect(x+width+padding,y,width,height),"Capture Front Photo")){
                StartCoroutine(TakePhoto());
            }
        }
    }
    IEnumerator TakePhoto()  // Start this Coroutine on some button click
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
        //Write out the PNG. Of course you have to substitute your_path for something sensible
        WWWForm form = new WWWForm();
        form.AddField("frameCount", Time.frameCount.ToString());
        form.AddBinaryData("fileUpload", bytes);

        // Upload to a cgi script
        var w = UnityWebRequest.Post("http://10.144.44.118:8080", form);
        yield return w.SendWebRequest();
        if (w.isNetworkError || w.isHttpError)
            print(w.error);
        else
            print("Finished Uploading Screenshot");
        yield return null;
        // send to server
    }
}
