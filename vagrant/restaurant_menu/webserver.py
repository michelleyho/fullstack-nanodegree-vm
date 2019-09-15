from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi

#   importing basic CRUD Operations with sqlalchemy
from database_setup import Base, Restaurant, MenuItem
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

#   Create session and connect to DB
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        try:
            if self.path.endswith("delete"):
                restaurantIDPath = self.path.split("/")[2]
                targetRestaurant = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if targetRestaurant != []:
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()

                    output = "<html><body>"
                    output += "<h1>Are you sure you want to delete %s?</h1>"%(targetRestaurant.name)
                    output += "<form method='POST' enctype='multipart/form-data' action='restaurants/%s/delete'>"%(restaurantIDPath)
                    output += "<input type='submit' value='Delete'>"
                    output += "</body></html>"
                    
                    self.wfile.write(output)
                    print output
                    return

            if self.path.endswith("/edit"):
                restaurantIDPath = self.path.split("/")[2]
                targetRestaurant = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                # Found targetRestaurant to edit
                if targetRestaurant != []:
                    self.send_response(200)
                    self.send_header('Content-type','text/html')
                    self.end_headers()  
                    
                    output = "<html><body>"
                    output += "<h1>"
                    output += targetRestaurant.name
                    output += "<form method='POST' enctype='multipart/form-data' action='restaurants/%s/edit'>"%(restaurantIDPath)
                    output += "<input name='newRestaurantName' type='text' placeholder='%s'>"%(targetRestaurant.name)
                    output += "<input type='submit' value='Rename'>"
                    output += "</form>"
                    output += "</body></html>"
                
                    self.wfile.write(output)
                    print output
                    return
                 

            if self.path.endswith('/restaurants/new'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                output = ""
                output += "<html><body>"
                output += "<h1>Make a New Restaurant</h1>"
                output += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>"
                output += "<input name='newRestaurantName' type='text' placeholder= 'New Restaurant Name'>"
                output += "<input type='submit' value='Create'> </form>"
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return
                 
            if self.path.endswith('/restaurants'):
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                allRestaurants = session.query(Restaurant).all()
                
                output = ""
                output += "<html><body>"
                output += "<h1>Restaurants</h1>"
                output += "<a href='/restaurants/new'>Make a new restaurant </a><br><br>"
                for restaurant in allRestaurants:
                    output += restaurant.name + "<br>"
                    output += "<a href='/restaurants/%s/edit'>Edit</a><br>"%(restaurant.id)
                    output += "<a href='/restaurants/%s/delete'>Delete</a><br>"%(restaurant.id)
                output += "</body></html>"
                self.wfile.write(output)
                print output
                return

        except IOError:
            self.send_error(404, 'File Not Found: %s' % self.path)
    
    def do_POST(self):
        try:
            if self.path.endswith("delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                restaurantIDPath = self.path.split("/")[2]
                myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                if myRestaurantQuery != []:
                    session.delete(myRestaurantQuery)
                    session.commit()
                    
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

                    return
                
            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('newRestaurantName')
                    restaurantIDPath = self.path.split("/")[2]
                    
                    myRestaurantQuery = session.query(Restaurant).filter_by(id=restaurantIDPath).one()
                    if myRestaurantQuery != []:
                        myRestaurantQuery.name = messageContent[0]
                        session.add(myRestaurantQuery)
                        session.commit()
                        
                        self.send_response(301)
                        self.send_header('Content-type', 'text/html')
                        self.send_header('Location', '/restaurants')
                        self.end_headers()

                        return

                    
            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields=cgi.parse_multipart(self.rfile, pdict)
                    messageContent = fields.get('newRestaurantName')
                    
                    #Create new restaurant class
                    newRestaurant = Restaurant(name=messageContent[0])
                    session.add(newRestaurant)
                    session.commit()
                    
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()
                
                    return
        except:
            pass


def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()
