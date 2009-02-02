
public class OutterClass {
	private String a = initializeA();
	private String b = initializeB();
	
	
	private class PrivateInner implements MyInterface {
		@Override
		public void printHello() {
			System.out.println("Hello from private inner class");	
		}
	}
	
	public MyInterface getPrivateInnerClass() {
		return new PrivateInner();
	}
	
	public void printFields() {
		System.out.println("A=" + a + " B=" + b);
	}

	private final String initializeA() { return "A" + this.b; }
	
	private final String initializeB() { return "B" + this.a; }
	
	
}
