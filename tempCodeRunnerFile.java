import java.awt.event.*;
import javax.swing.*;
import javax.imageio.ImageIO;
import java.io.IOException;

public class simpleCalc {
    public static void main(String[] args) {
        JFrame frame = new JFrame("Simple Calculator");
        frame.setSize(600, 500);
        frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
        MyContainer container = new MyContainer();
        
        // Adding title label
        MyLabel title = new MyLabel("Mini Math Solver", 300, 50, 150, 30);
        container.addComponent(title.label);

        // Adding buttons
        MyButton btnAdd = new MyButton("ADD", 100, 25, 350, 100);
        container.addComponent(btnAdd.button);

        MyButton btnSub = new MyButton("SUBTRACT", 100, 25, 350, 150);
        container.addComponent(btnSub.button);

        // Event Handling for buttons
        btnAdd.button.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e1) {
                // Handle addition logic here
            }
        });

        btnSub.button.addActionListener(new ActionListener() {
            public void actionPerformed(ActionEvent e2) {
                // Handle subtraction logic here
            }
        });

        frame.add(container);
        frame.setVisible(true);
    }
}
