import java.io.FileWriter;
import java.io.FileReader;
import java.io.BufferedWriter;
import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.OutputStreamWriter;
import java.io.Writer;
import java.io.PrintWriter;

/* *** ODSATag: Link *** */
class Link {
  private Object e;
  private Link n;

  // Constructors
  Link(Object ine, Link inn) { e = ine; n = inn; }
  Link(Link inn) { e = null; n = inn; }

  public  Object element() { return e; }           // Return the value
  public void setelement(Object ine) { e = ine; } // Set element value
  public Link next() { return n; }                // Return next link
  public void setnext(Link inn) { n = inn; }      // Set next link
}
/* *** ODSAendTag: Link *** */

public class studentreassgnpntrPROG {

public static void main(String [ ] args) {

boolean SUCCESS = false;
  
  Link studentHead; 
  
  studentHead = reAssignPointer(); 
  
  Link Mthird = new Link(3,null); 
  Link Msecond = new Link(2,Mthird); 
  Link Mfirst = new Link(1,Msecond); 
	
  Link Mp; 
  Link Mr; 
	
  Mp = Mfirst;
  
  Mp = Mp.next();  
  
  if (Mp.element() == studentHead.element()) SUCCESS = true;

  try{

  
  PrintWriter output = new PrintWriter("output", "UTF-8");



   if (SUCCESS) { 
   
     output.println("Well Done!");
     output.close();
   }
   else 
   {
     output.println("Try Again! You have either disconnected a link or incorrectly reassigned the variable p.");
     output.close();
      
   }
   
  }
  catch (IOException e) {
	e.printStackTrace();
  }


}

public static boolean checkIfLinksLinked(Link front, Link middle, Link end){
    
    Object one = 1;
    Object two = 2; 
    Object three = 3; 
    
    boolean linkFlag = false; 
    
    if(front.next() == middle) 
    {
        if(middle.next() == end) 
        {
            if(end.next () == null)
            {
                linkFlag = true; 
            }
            else 
            {
                linkFlag = false; 
            }
        }
        else 
        {
            linkFlag = false; 
        }
    }
    else 
    {
        linkFlag = false; 
    }
    
    return linkFlag; 
}



public static Link reAssignPointer() {
	
	Link returnLink; 

 
