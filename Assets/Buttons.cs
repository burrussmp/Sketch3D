using UnityEngine;
using System.Collections;
using UnityEngine.UI;
public class Buttons : MonoBehaviour
{
    private bool detected;
    public int selGridInt;
    void OnGUI()
    {
        GameObject parent = GameObject.Find("newObject");
        detected = parent.transform.childCount != 0;
        if (detected){
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
                    Rotate(1,-10f);
                }
            }
            if (GUI.Button(new Rect(x+width+padding,y,width,height),"+X Axis")){
                if (selGridInt == 0){
                    Translate(1,0.01f);
                } else if (selGridInt == 1){
                    Scale(1,0.05f);
                } else if (selGridInt == 2){
                    Rotate(1,10f);
                }
            }
            if (GUI.Button(new Rect(x,y+height+padding,width,height),"-Y Axis")){
                if (selGridInt == 0){
                    Translate(2,-0.01f);
                } else if (selGridInt == 1){
                    Scale(2,-0.05f);
                } else if (selGridInt == 2){
                    Rotate(2,-10f);
                }
            }
            if (GUI.Button(new Rect(x+width+padding,y+height+padding,width,height),"+Y Axis")){
                if (selGridInt == 0){
                    Translate(2,0.01f);
                } else if (selGridInt == 1){
                    Scale(2,0.05f);
                } else if (selGridInt == 2){
                    Rotate(2,10f);
                }
            }
            if (GUI.Button(new Rect(x,y+2*height+2*padding,width,height),"-Z Axis")){
                if (selGridInt == 0){
                    Translate(3,-0.01f);
                } else if (selGridInt == 1){
                    Scale(3,-0.05f);
                } else if (selGridInt == 2){
                    Rotate(3,-10f);
                }
            }
            if (GUI.Button(new Rect(x+width+padding,y+2*height+2*padding,width,height),"+Z Axis")){
                if (selGridInt == 0){
                    Translate(3,0.01f);
                } else if (selGridInt == 1){
                    Scale(3,0.05f);
                } else if (selGridInt == 2){
                    Rotate(3,10f);
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
        }
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
        Vector3 euler = parent_rotate.eulerAngles;
        if (input == 1){
            euler.x = euler.x + change;
            parent.transform.rotation = Quaternion.Euler(euler.x, euler.y, euler.z);;
        } else if (input == 2){
            euler.y = euler.y + change;
            parent.transform.rotation = Quaternion.Euler(euler.x, euler.y, euler.z);;
        } else {
            euler.z = euler.z + change;
            parent.transform.rotation = Quaternion.Euler(euler.x, euler.y, euler.z);;
        }
    }

}
