import java.util.Map;
import java.util.TreeMap;

/**
 * The HelloWorldApp class implements an application that
 * simply prints "Hello World" to standard output.
 * 
 * @author tmacam
 *
 */
public class HelloWorldApp {

	/**
	 * @param args Program arguments.
	 */
	public static void main(String[] args) {

		System.out.println("Hello, World!"); // Display the string
		
		String comment = "This program was called with ";
		comment += args.length;
		comment += " arguments.";
		
		System.out.println(comment);
		
		countWord(args);
		
		OutterClass outter = new OutterClass();
		outter.printFields();
		
		MyInterface private_thing = outter.getPrivateInnerClass();
		private_thing.printHello();
		
	}
	
	public static void countWord(String[] args) {
		Map<String, Integer> m = new TreeMap<String, Integer>();
		for (String word: args) {
			Integer freq = m.get(word);
			m.put(word, (freq == null) ? 1 : freq + 1);
		}
		System.out.println(m);
	}

}
