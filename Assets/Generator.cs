using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.UI;
using UnityEngine.Networking;
using UnityEngine;
using System.Collections.Generic;
using System;
using System.Linq;
using System.Collections.Generic;

public class Generator : MonoBehaviour
{    // Start is called before the first frame update

    public List<List<float>> mList;
    public static bool inFirst;
    public static bool inSecond;
    public static bool detected;
    public GameObject gameObject;
    void Start()
    {
        StartCoroutine(GetData());
        StartCoroutine(CreateMesh());
        //var materialList = new List<Material>();
    }

    // Update is called once per frame
    void Update()
    {
        
    }
    IEnumerator CreateMesh(){
        while(inFirst)       
            yield return new WaitForSeconds(0.1f);
        int meshID = 97;
        int cur = 0;
        var resources = Resources.FindObjectsOfTypeAll(typeof(Material));
        foreach(var face in mList){
            int num_of_vertices = Convert.ToInt32(face[face.Count-1]);
            Vector2[] vertices2D = new Vector2[num_of_vertices];
            int j = 0;
            for (int i = 0; i < face.Count-1; i=i+3){
                if (cur < 4){
                    vertices2D[j] = new Vector2(face[i],face[i+1]);
                } else {
                    vertices2D[j] = new Vector2(face[i],face[i+2]);
                }
                j = j +1;
            }
            Triangulator tr = new Triangulator(vertices2D);
            int[] indices = tr.Triangulate();
            Vector3[] vertices = new Vector3[vertices2D.Length];
            j =0;
            Debug.Log(cur);
            for (int i = 0; i < face.Count-1; i=i+3){

                if (cur < 4){
                    vertices[j] = new Vector3(vertices2D[j].x, vertices2D[j].y,face[i+2]);
                } else {
                    vertices[j] = new Vector3(vertices2D[j].x, face[i+1],vertices2D[j].y);
                }
                Debug.Log(vertices[j]);
                j = j + 1;
            }
            Mesh msh = new Mesh();
            msh.vertices = vertices;
            msh.triangles = indices;
            msh.RecalculateNormals();
            msh.RecalculateBounds();
            // Set up game object with mesh;
            gameObject = GameObject.Find("newObject");

            GameObject child = new GameObject(Char.ToString(Convert.ToChar(meshID)));
            MeshRenderer render = child.AddComponent<MeshRenderer>();
            render.materials[0] = gameObject.GetComponent<Renderer>().material;
            child.transform.parent = gameObject.transform;

            MeshFilter filter = child.AddComponent<MeshFilter>();
            filter.mesh = msh;
            cur = cur + 1;
            meshID = meshID + 1;
            msh = new Mesh();
            msh.vertices = vertices;
            msh.triangles = indices;
            msh.RecalculateNormals();
            msh.RecalculateBounds();

            child = new GameObject(Char.ToString(Convert.ToChar(meshID)));
            render = child.AddComponent<MeshRenderer>();
            render.materials[0] = gameObject.GetComponent<Renderer>().material;
            child.transform.parent = gameObject.transform;
            filter = child.AddComponent<MeshFilter>();
            filter.mesh = msh;
            cur = cur + 1;
            if (filter != null)
            {
                Mesh mesh = filter.mesh;
    
                Vector3[] normals = mesh.normals;
                for (int i=0;i<normals.Length;i++)
                    normals[i] = -normals[i];
                mesh.normals = normals;
    
                for (int m=0;m<mesh.subMeshCount;m++)
                {
                    int[] triangles = mesh.GetTriangles(m);
                    for (int i=0;i<triangles.Length;i+=3)
                    {
                        int temp = triangles[i + 0];
                        triangles[i + 0] = triangles[i + 1];
                        triangles[i + 1] = temp;
                    }
                    mesh.SetTriangles(triangles, m);
                }
            }
            meshID = meshID + 1;
        }
        inSecond = false;
        detected = true;
    }
    IEnumerator GetData() {
            inFirst = true;
            inSecond = true;
			// Play audio when target is found
            UnityWebRequest www = UnityWebRequest.Get("http://10.0.0.118:8080");
			yield return www.SendWebRequest();

            if(www.isNetworkError || www.isHttpError) {
                Debug.Log(www.error);
            }
            else {
                // Show results as text
                Debug.Log(www.downloadHandler.text);
                string inputTextString = www.downloadHandler.text;
                int next = 0;
                var list = new List<List<float>>();
                while (next != -1){
                    int start = inputTextString.IndexOf('N',next);
                    int num_delimiter = inputTextString.IndexOf(',',start);
                    next = inputTextString.IndexOf('N',start+1);
                    int num_samples = Int16.Parse(inputTextString.Substring(start+1,num_delimiter-start-1));
                    string sub_input;
                    if (next != -1){
                        sub_input = inputTextString.Substring(num_delimiter+1,next-num_delimiter-1);
                    } else {
                        sub_input = inputTextString.Substring(num_delimiter+1,inputTextString.Length-num_delimiter-1);
                    }
                    sub_input = sub_input.Replace("[","");
                    sub_input = sub_input.Replace("]","");
                    var myList = sub_input.Split(',').Select(Convert.ToSingle).ToList();
                    myList.Add(Convert.ToSingle(num_samples));
                    list.Add(myList);
                }
                                // foreach(var j in list){
                //     foreach(var i in j){
                //         Debug.Log(i);
                //     }
                // }
                mList = list;
                inFirst = false;
            }

        }
    }



public class Triangulator
{
    private List<Vector2> m_points = new List<Vector2>();
 
    public Triangulator (Vector2[] points) {
        m_points = new List<Vector2>(points);
    }
 
    public int[] Triangulate() {
        List<int> indices = new List<int>();
 
        int n = m_points.Count;
        if (n < 3)
            return indices.ToArray();
 
        int[] V = new int[n];
        if (Area() > 0) {
            for (int v = 0; v < n; v++)
                V[v] = v;
        }
        else {
            for (int v = 0; v < n; v++)
                V[v] = (n - 1) - v;
        }
 
        int nv = n;
        int count = 2 * nv;
        for (int v = nv - 1; nv > 2; ) {
            if ((count--) <= 0)
                return indices.ToArray();
 
            int u = v;
            if (nv <= u)
                u = 0;
            v = u + 1;
            if (nv <= v)
                v = 0;
            int w = v + 1;
            if (nv <= w)
                w = 0;
 
            if (Snip(u, v, w, nv, V)) {
                int a, b, c, s, t;
                a = V[u];
                b = V[v];
                c = V[w];
                indices.Add(a);
                indices.Add(b);
                indices.Add(c);
                for (s = v, t = v + 1; t < nv; s++, t++)
                    V[s] = V[t];
                nv--;
                count = 2 * nv;
            }
        }
 
        indices.Reverse();
        return indices.ToArray();
    }
 
    private float Area () {
        int n = m_points.Count;
        float A = 0.0f;
        for (int p = n - 1, q = 0; q < n; p = q++) {
            Vector2 pval = m_points[p];
            Vector2 qval = m_points[q];
            A += pval.x * qval.y - qval.x * pval.y;
        }
        return (A * 0.5f);
    }
 
    private bool Snip (int u, int v, int w, int n, int[] V) {
        int p;
        Vector2 A = m_points[V[u]];
        Vector2 B = m_points[V[v]];
        Vector2 C = m_points[V[w]];
        if (Mathf.Epsilon > (((B.x - A.x) * (C.y - A.y)) - ((B.y - A.y) * (C.x - A.x))))
            return false;
        for (p = 0; p < n; p++) {
            if ((p == u) || (p == v) || (p == w))
                continue;
            Vector2 P = m_points[V[p]];
            if (InsideTriangle(A, B, C, P))
                return false;
        }
        return true;
    }
 
    private bool InsideTriangle (Vector2 A, Vector2 B, Vector2 C, Vector2 P) {
        float ax, ay, bx, by, cx, cy, apx, apy, bpx, bpy, cpx, cpy;
        float cCROSSap, bCROSScp, aCROSSbp;
 
        ax = C.x - B.x; ay = C.y - B.y;
        bx = A.x - C.x; by = A.y - C.y;
        cx = B.x - A.x; cy = B.y - A.y;
        apx = P.x - A.x; apy = P.y - A.y;
        bpx = P.x - B.x; bpy = P.y - B.y;
        cpx = P.x - C.x; cpy = P.y - C.y;
 
        aCROSSbp = ax * bpy - ay * bpx;
        cCROSSap = cx * apy - cy * apx;
        bCROSScp = bx * cpy - by * cpx;
 
        return ((aCROSSbp >= 0.0f) && (bCROSScp >= 0.0f) && (cCROSSap >= 0.0f));
    }
}