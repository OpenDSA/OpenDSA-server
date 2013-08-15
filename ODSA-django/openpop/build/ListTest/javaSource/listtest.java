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
/* *** ODSATag: AList *** */
// Array-based list implementation
/* *** ODSATag: AListVars *** */
class AList implements List {
  private Object listArray[];             // Array holding list elements
  private static final int defaultSize = 10; // Default size
  private int maxSize;                    // Maximum size of list
  private int listSize;                   // Current # of list items
  private int curr;                       // Position of current element
/* *** ODSAendTag: AListVars *** */

  // Constructors
  // Create a new list object with maximum size "size"
  AList(int size) { 
    maxSize = size;
    listSize = curr = 0;
    listArray = new Object[size];         // Create listArray
  }
  // Create a list with the default capacity
  AList() { this(defaultSize); }          // Just call the other constructor

  public void clear()                     // Reinitialize the list
    { listSize = curr = 0; }              // Simply reinitialize values

/* *** ODSATag: AListInsert *** */
  // Insert "it" at current position
  public void insert(Object it) {
    if (listSize >= maxSize) return;
    for (int i=listSize; i>curr; i--)  // Shift elements up
      listArray[i] = listArray[i-1];   //   to make room
    listArray[curr] = it;
    listSize++;                        // Increment list size
  }
/* *** ODSAendTag: AListInsert *** */

/* *** ODSATag: AListAppend *** */
  // Append "it" to list
 public  void append(Object it) {
    if (listSize >= maxSize) return;
    listArray[listSize++] = it;
  }
/* *** ODSAendTag: AListAppend *** */

/* *** ODSATag: AListRemove *** */
  // Remove and return the current element
 public Object remove() {
    if ((curr<0) || (curr>=listSize))  // No current element
      return null;
    Object it = listArray[curr];       // Copy the element
    for(int i=curr; i<listSize-1; i++) // Shift them down
      listArray[i] = listArray[i+1];
    listSize--;                        // Decrement size
    return it;
  }
/* *** ODSAendTag: AListRemove *** */

  public void moveToStart() { curr = 0; }       // Set to front
  public void moveToEnd() { curr = listSize; }  // Set at end
  public void prev() { if (curr != 0) curr--; } // Move left
  public void next() { if (curr < listSize) curr++; } // Move right
  public int length() { return listSize; }      // Return list size
  public int currPos() { return curr; }         // Return current position
  
  // Set current list position to "pos"
  public   void moveToPos(int pos) {
    if ((pos < 0) || (pos > listSize)) return;
    curr = pos;
  }

  // Return true if current position is at end of the list
  public Boolean isAtEnd() { return curr == listSize; }

  // Return the current element
  public Object getValue() {
    if ((curr < 0) || (curr >= listSize)) // No current element
      return null;
    return listArray[curr];
  }
}
/* *** ODSAendTag: AList *** */

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

/* *** ODSATag: ListADT *** */
interface List { // List class ADT
  // Remove all contents from the list, so it is once again empty
  public  void clear();

  // Insert "item" at the current location
  // The client must ensure that the list's capacity is not exceeded
  public void insert(Object item);

  // Append "item" at the end of the list
  // The client must ensure that the list's capacity is not exceeded
  public  void append(Object item);

  // Remove and return the current element
  public Object remove();

  // Set the current position to the start of the list
  public  void moveToStart();

  // Set the current position to the end of the list
  public void moveToEnd();

  // Move the current position one step left, no change if already at beginning
  public void prev();

  // Move the current position one step right, no change if already at end
  public void next();

  // Return the number of elements in the list
  public int length();

  // Return the position of the current element
  public int currPos();

  // Set the current position to "pos"
  public void moveToPos(int pos);

  // Return true if current position is at end of the list
  public Boolean isAtEnd();

  // Return the current element
  public Object getValue();
}
/* *** ODSAendTag: ListADT *** */

/* *** ODSATag: LList *** */
// Linked list implementation
/* *** ODSATag: LListVars *** */
class LList implements List {
  private Link head;         // Pointer to list header
  private Link tail;         // Pointer to last element
  protected Link curr;       // Access to current element
  private int listSize;      // Size of list
/* *** ODSAendTag: LListVars *** */

/* *** ODSATag: LListCons *** */
  // Constructors
  LList(int size) { this(); }   // Constructor -- Ignore size
  LList() { clear(); }

  // Remove all elements
  public void clear() {
    curr = tail = new Link(null); // Create trailer
    head = new Link(tail);        // Create header
    listSize = 0;
  }
/* *** ODSAendTag: LListCons *** */
  
/* *** ODSATag: LListInsert *** */
  // Insert "it" at current position
  public  void insert(Object it) {
    curr.setnext(new Link(curr.element(), curr.next()));
    curr.setelement(it);
    if (tail == curr) tail = curr.next();  // New tail
    listSize++;
  }
/* *** ODSAendTag: LListInsert *** */
  
  // Append "it" to list
  public void append(Object it) {
    tail.setnext(new Link(null));
    tail.setelement(it);
    tail = tail.next();
    listSize++;
  }

/* *** ODSATag: LListRemove *** */
  // Remove and return current element
  public  Object remove () {
    if (curr == tail) return null;          // Nothing to remove
    Object it = curr.element();             // Remember value
    curr.setelement(curr.next().element()); // Pull forward the next element
    if (curr.next() == tail) tail = curr;   // Removed last, move tail
    curr.setnext(curr.next().next());       // Point around unneeded link
    listSize--;                             // Decrement element count
    return it;                              // Return value
  }
/* *** ODSAendTag: LListRemove *** */

  public void moveToStart() { curr = head.next(); } // Set curr at list start
  public void moveToEnd() { curr = tail; }     // Set curr at list end

  // Move curr one step left; no change if now at front
  public  void prev() {
    if (head.next() == curr) return; // No previous element
    Link temp = head;
    // March down list until we find the previous element
    while (temp.next() != curr) temp = temp.next();
    curr = temp;
  }

  // Move curr one step right; no change if now at end
  public  void next() { if (curr != tail) curr = curr.next(); }

  public int length() { return listSize; } // Return list length


  // Return the position of the current element
  public  int currPos() {
    Link temp = head.next();
    int i;
    for (i=0; curr != temp; i++)
      temp = temp.next();
    return i;
  }

  // Move down list to "pos" position
  public void moveToPos(int pos) {
    if ((pos < 0) || (pos > listSize)) {
      //println("Pos out of range, current position unchanged");
      return;
    }
    curr = head.next();
    for(int i=0; i<pos; i++) curr = curr.next();
  }

  // Return true if current position is at end of the list
  public  Boolean isAtEnd() { return curr == tail; }

  // Return current element value
  public Object getValue() {
    if(curr == tail) return null;
    return curr.element();
  }
}
/* *** ODSAendTag: LList *** */

public class studentlisttest {

public static void main(String [ ] args) {
String Mstring = null;
try{
BufferedReader reader = new BufferedReader(new FileReader("generatedlist"));
Mstring = reader.readLine();

}
catch (IOException e) {
	e.printStackTrace();
}

boolean SUCCESS = false;
  //LList Lmodel = new LList();
    LList Lstudent = new LList();
  //Lmodel.moveToStart();
  //Lmodel.insert(5);
  //Lmodel.insert(7);
  //Lmodel.next();
  //Lmodel.next();
  //Lmodel.insert(3);
  //Lmodel.insert(17);
  //String Mstring = toString(Lmodel);
  exercise1(Lstudent);
  String Mstudent = toString(Lstudent);
  if (Mstring.equals( Mstudent)) SUCCESS = true;

  try{

  
  PrintWriter output = new PrintWriter("output", "UTF-8");



   if (SUCCESS) { 
   
     output.println("Well Done!");
     output.close();
   }
   else 
   {
     output.println("Try Again!  Expected Answer is"+Mstring +" Your Answer is: " + Mstudent );
     output.close();
      
   }
   
  }
  catch (IOException e) {
	e.printStackTrace();
  }


}

public static String toString(List L) {
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

 
