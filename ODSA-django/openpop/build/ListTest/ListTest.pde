boolean SUCCESS = false;
import java.io.File;
import java.io.FileOutputStream;
import java.io.PrintWriter;
import java.io.FileNotFoundException;

String toString(List L) {
  // Save the current position of the list
  int oldPos = L.currPos();
  StringBuffer out = new StringBuffer((L.length() + 1) * 4);

  L.moveToStart();
  out.append("< ");
  for (int i = 0; i < oldPos; i++) {
    out.append(L.getValue());
    out.append(" ");
    L.next();
  }
  out.append("| ");
  for (int i = oldPos; i < L.length(); i++) {
    out.append(L.getValue());
    out.append(" ");
    L.next();
  }
  out.append(">");
  L.moveToPos(oldPos); // Reset the fence to its original position
  return out.toString();
}

void setup() {
  LList Lmodel = new LList();
  LList Lstudent = new LList();
  Lmodel.moveToStart();
  Lmodel.insert(5);
  Lmodel.insert(7);
  Lmodel.next();
  Lmodel.next();
  Lmodel.insert(3);
  Lmodel.insert(17);
  String Mstring = toString(Lmodel);
  exercise1(Lstudent);
  String Mstudent = toString(Lstudent);
  if (Mstring.equals( Mstudent)) SUCCESS = true;
  
  PrintWriter output = createWriter("output");
  if (SUCCESS) { 
   
     output.println("Well Done!");
     output.flush();
     output.close();
   }
  else 
  {
     output.println("Try Again!  Expected Answer is"+Mstring +" Your Answer is: " + Mstudent );
     output.flush();
     output.close();
      
  }
   
   exit();
  }
  
