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
    private int[] distVector = new int[RouterSimulator.NUM_NODES];

    private boolean poisonedReverseEnabled = false;
    //--------------------------------------------------
    public RouterNode(int ID, RouterSimulator sim, int[] costs) {
        myID = ID;
        this.sim = sim;
        myGUI =new GuiTextArea("  Output window for Router #"+ ID + "  ");

        System.arraycopy(costs, 0, this.costs, 0, RouterSimulator.NUM_NODES);
        System.arraycopy(costs, 0, distVector, 0, RouterSimulator.NUM_NODES);

        // Find routes to neighbors
        for(int i = 0; i < RouterSimulator.NUM_NODES; i++) {
            if(this.costs[i] != RouterSimulator.INFINITY) {
                // This is a neighbour, next hop is known
                this.routes[i] = i;
                if(i != this.myID) {
                    this.numNeighbors++;
                }
            }
            else {
                this.routes[i] = RouterSimulator.INFINITY; // Unknown route
            }
        }

        this.neighbors = new int[numNeighbors];
        int iNeighbor = 0;
        for(int i = 0; i < RouterSimulator.NUM_NODES; i++) {
            if(i == myID) {
                continue;
            }
            if(this.costs[i] != RouterSimulator.INFINITY){
                neighbors[iNeighbor] = i;
                iNeighbor++;
            }
        }

        this.distTable = new int[numNeighbors][RouterSimulator.NUM_NODES];
        for(int i = 0; i < numNeighbors; i++) {
            for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
                if(neighbors[i] == j) {
                    distTable[i][j] = 0;
                } else {
                    distTable[i][j] = RouterSimulator.INFINITY;
                }
                // No idea about neighbors distance to anywhere, even ourself (sic!)
            }
        }

        printDistanceTable();

        for(int i = 0; i < this.neighbors.length; i++) {
            sendUpdate(new RouterPacket(this.myID, this.neighbors[i], this.costs));
        }

    }

    //--------------------------------------------------
    public void recvUpdate(RouterPacket pkt) {

        if(pkt.destid == this.myID) {
            distTable[java.util.Arrays.binarySearch(neighbors, pkt.sourceid)] = pkt.mincost;
        }

        recomputeCostsAndRoutesVectors();
    }


    //--------------------------------------------------
    private void sendUpdate(RouterPacket pkt) {
        sim.toLayer2(pkt);
    }


    //--------------------------------------------------
    public void printDistanceTable() {
        F formatter = new F();
        myGUI.println("Current table for " + myID +
                      "  at time " + sim.getClocktime());

        myGUI.println("Distancetable:");
        String dstTableHeader = new String();
        dstTableHeader = "    dst |";
        for(int i = 0; i < RouterSimulator.NUM_NODES; i++) {
            dstTableHeader += "    " + i;
        }

        // Print distance table
        myGUI.println(dstTableHeader);
        myGUI.println(new String(new char[dstTableHeader.length()]).replace("\0", "-"));

        for(int i = 0; i < neighbors.length; i++) {
            String dstString = new String();
            dstString = " nbr " + neighbors[i] + "  |";

            for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
                dstString += formatter.format(distTable[i][j], 5);
            }
            myGUI.println(dstString);
        }

        // Print cost and route vectors
        myGUI.println("Our distance vector and routes:");
        myGUI.println(dstTableHeader);
        myGUI.println(new String(new char[dstTableHeader.length()]).replace("\0", "-"));

        String costString = new String();
        String routeString = new String();
        costString = " dist   |";
        routeString = " route  |";

        for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
            costString += formatter.format(distVector[j], 5);
            if(routes[j] == RouterSimulator.INFINITY) {
                routeString += formatter.format("-", 5);
            } else {
                routeString += formatter.format(routes[j], 5);
            }
        }

        myGUI.println(costString);
        myGUI.println(routeString);
        myGUI.println();


    }

    //--------------------------------------------------
    public void updateLinkCost(int dest, int newcost) {
        costs[dest] = newcost;
        recomputeCostsAndRoutesVectors();
    }

    private void recomputeCostsAndRoutesVectors() { // THIS IS JAAAAVAAAA!
        boolean somethingChanged = false;

        for(int j = 0; j < RouterSimulator.NUM_NODES; j++) {
            int shortestPathFound = RouterSimulator.INFINITY;
            int nextHop = -1;

            if(j == myID) {
                shortestPathFound = 0;
                nextHop = myID;
                continue;
            }

            // Shortest path, if we first route through a neighbour
            for(int i = 0; i < neighbors.length; i++) {

                if(costs[neighbors[i]] + distTable[i][j] < shortestPathFound) {
                    shortestPathFound = costs[neighbors[i]] + distTable[i][j];
                    nextHop = neighbors[i];
                }
            }

            if(shortestPathFound != distVector[j]) {
                somethingChanged = true;
                distVector[j] = shortestPathFound;
                routes[j] = nextHop;
            }
        }

        if(somethingChanged) {
            sendUpdatesToAllTheOtherRouterNodes();
        }

        printDistanceTable();
    }

    private void sendUpdatesToAllTheOtherRouterNodes() {
        for(int i = 0; i < this.neighbors.length; i++) {
            int[] poisonedReversedCosts = new int[RouterSimulator.NUM_NODES];
            System.arraycopy(distVector, 0, poisonedReversedCosts, 0, distVector.length);

            if(poisonedReverseEnabled){
                for(int j = 0; j < routes.length; j++) {
                    if(neighbors[i] == routes[j] && j != neighbors[i]) {
                        poisonedReversedCosts[j] = RouterSimulator.INFINITY;
                    }
                }
            }
            sendUpdate(new RouterPacket(myID, neighbors[i], poisonedReversedCosts));
        }
    }

}
