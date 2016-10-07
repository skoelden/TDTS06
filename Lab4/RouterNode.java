import javax.swing.*;

public class RouterNode {
    private int myID;
    private GuiTextArea myGUI;
    private RouterSimulator sim;
    private int[] costs = new int[RouterSimulator.NUM_NODES];
    private int[] routes = new int[RouterSimulator.NUM_NODES];
    private int numNeighbors;
    private int[] neighbors;
    private int[][] distTable;

    //--------------------------------------------------
    public RouterNode(int ID, RouterSimulator sim, int[] costs) {
        myID = ID;
        this.sim = sim;
        myGUI =new GuiTextArea("  Output window for Router #"+ ID + "  ");

        System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);

        // Find routes to neighbors
        for(int i = 0; i < RouterSimulator.NUM_NODES; i++) {
            if(this.costs[i] != RouterSimulator.INFINITY) {
                // This is a neighbour, next hop is known
                this.routes[i] = i;
                this.numNeighbors++;
            }
            else {
                this.routes[i] = RouterSimulator.INFINITY; // Unknown route
            }
        }

        this.neighbors = new int[numNeighbors];
        int iNeighbor = 0;
        for(int i = 0; i < RouterSimulator.NUM_NODES; i++) {
            if(this.costs[i] != RouterSimulator.INFINITY){
                neighbors[iNeighbor] = i;
                iNeighbor++;
            }
        }

        this.distTable = new int[numNeighbors][RouterSimulator.NUM_NODES];
        for(int i = 0; i < numNeighbors; i++) {
            for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
                this.distTable[i][j] = RouterSimulator.INFINITY;
                // No idea about neighbors distance to anywhere, even ourself (sic!)
            }
        }

        printDistanceTable();

    }

    //--------------------------------------------------
    public void recvUpdate(RouterPacket pkt) {


    }


    //--------------------------------------------------
    private void sendUpdate(RouterPacket pkt) {
        sim.toLayer2(pkt);

    }


    //--------------------------------------------------
    public void printDistanceTable() {
        myGUI.println("Current table for " + myID +
                      "  at time " + sim.getClocktime());

        myGUI.println("Disojsdfotancetable:");
    }

    //--------------------------------------------------
    public void updateLinkCost(int dest, int newcost) {
        costs[dest] = newcost;
    }

}
