
int SIZE = 600;

int scale = 150;
int buf = 10;
float R, theta;
float[] r;
String[] labels;

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
    
    void draw() {
        
        noStroke();
        fill(this.r,this.g,this.b);
        ellipse(this.x,this.y,2*this.radius,2*this.radius);
    }
    
    String process() {
        float dist;
        dist = abs(mouseX - this.x)*abs(mouseX - this.x) + abs(mouseY - this.y)*abs(mouseY - this.y);
        dist = sqrt(dist);
        
        String l;
        if ( this.radius > 10 && dist < this.radius )
        {

            l = this.label;
        }
        return l;
    }

}

Dot[] dots ;
int n;

void setup()
{
    size(SIZE+200,SIZE);
    textSize(25);
    background(255);
    String[] lines = loadStrings("data.txt");
  
    n = lines.length;
    int x,y,r,d;
    float angle,value;
    String name;
    dots = new Dot[lines.length];
    for(int i = 0; i < n; i++)
    {
        String[] words = split(lines[i], ",");
        value = float(words[1]);
        name = words[0];
        r = value*SIZE/2;
        d = (SIZE/2-r)
        angle = random(360)*PI/180
        x = d*sin(angle);
        y = d*cos(angle);
        dots[i] = new Dot(SIZE/2-x,SIZE/2-y,r,name);
        //println(this.label);
    }
    
    ;
    noStroke();
    smooth();
    for ( i=0; i<n;i++)
    {
        dots[i].draw();
        //dots[i].process();
    }

}


void draw() 
{
    String label;
    String temp;
    Dot select;
    //background(255);

    //fill(255,255,255);
    //stroke(0,0,0)
    
    //text('hello',100,100,1000,50);
    fill(255,255,255)
    rect(SIZE,0,200,SIZE);
    for ( i=0; i<n;i++)
    {
        //dots[i].draw();
        temp = dots[i].process();
        if (temp != null)
        {
            label = temp
            select = dots[i];
        }
    }
    if ( select != null ) {
        textSize(25);
        fill(select.r,select.g,select.b);
        text(label,SIZE,200);
    //println(label);
    }
}
