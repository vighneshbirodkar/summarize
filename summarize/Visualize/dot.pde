
int SIZE = 600;
int PANEL = 400;
Dot[] dots ;
int n;

/*
 * Class representing each Dot placed on canvas
 *
*/
class Dot {

    int x;
    int y;
    String label;
    int r,g,b;
    int radius;

    Dot(int x,int y,int radius,String label) {
        this.x = x;
        this.y = y;
        this.r = random(255);
        this.g = random(255);
        this.b = random(255);
        this.radius = radius;
        this.label = label;
        
    }
    
    /*
     *Draws the Dot on Canvas
     */
    void draw() {
        
        noStroke();
        fill(this.r,this.g,this.b);
        ellipse(this.x,this.y,2*this.radius,2*this.radius);
    }
    
    /*
     * Returns the dot's label if the mouse pointer is within its range
     */
    String process() {
        float dist;
        dist = abs(mouseX - this.x)*abs(mouseX - this.x) + abs(mouseY - this.y)*abs(mouseY - this.y);
        dist = sqrt(dist);
        
        String l;
        if ( this.radius > 0 && dist < this.radius ) {

            l = this.label;
        }
        return l;
    }

}



void setup() {
    
    int x,y,r,d;
    float angle,value;
    String name;

    size(SIZE+PANEL,SIZE);
    background(255);

    String[] lines = loadStrings("dot.vdf");
    n = lines.length;

    dots = new Dot[n];
    
    for(int i = 0; i < n; i++) {
        
        String[] words = split(lines[i], ",");
        
        value = float(words[1]);
        name = words[0];
        
        //radius of dot
        r = value*SIZE/2;

        //distance of dot from center
        d = (SIZE/2-r)
        
        //place dot at random polar angle
        angle = random(360)*PI/180
        
        x = d*sin(angle);
        y = d*cos(angle);
        dots[i] = new Dot(SIZE/2-x,SIZE/2-y,r,name);
    }
    
    noStroke();
    smooth();

    for ( i=0; i<n;i++) 
        dots[i].draw();

}


void draw() {
    String label;
    String temp;
    Dot select;

    
    fill(255,255,255)
    rect(SIZE,0,PANEL,SIZE);

    //check if the mouse is inside any dot
    for ( i=0; i<n;i++) {
        temp = dots[i].process();
        if (temp != null) {
            label = temp
            select = dots[i];
        }
    }
    //show the label
    if ( select != null ) {
        textSize(40);
        fill(select.r,select.g,select.b);
        text(label,SIZE+20,SIZE/2);
    }
}
