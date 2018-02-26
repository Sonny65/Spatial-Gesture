// Blade2Dance_2.0.cpp : Defines the entry point for the console application.
//Some parts of code was adapted from StackOverflow.com and microsoft.com
//dirent.h library credit is given in the header file
//Author: Arman Kapbasov (UC Davis)
//Outputs to the path of the configuration file

//--------------------Format of Configuartion file (.txt)--------------
//see attached Release_Information file
/*
1) Input can be either manual as the example below:

//--------------------Format of Configuartion file (.txt)--------------
//Blade_2_Dance Converter 2.0
//Number of files(or 0 for folder): N
//Dance_file: /path/
//Blade_File1/folder: /path/
//Finger_file1(pathfile or n/a): /path/
//Blade_File2: /path/
//Finger_file2(pathfile or n/a): /path/
///...
//Blade_FileN: /path/
//Finger_fileN(pathfile or n/a): /path/

2) Input can be a folder/directory (only 1 finger data file can be specified for all the data)
Example below:

//--------------------Format of Configuartion file (.txt)--------------
//Blade_2_Dance Converter 2.0
//Number of files(or 0 for folder): 0
//Dance_file: /path/
//Blade_file: /path/folder/
//Finger_file(pathfile or n/a): n/a

*/
//-----------------------------------------------------------------

#include "stdafx.h"
#include <iostream>
#include <fstream>
#include <stdlib.h>
#include <string>
#include <map>
#include <iomanip>
#include <windows.h>
#include <commdlg.h>
#include "dirent.h"


#define DOFBlade 50
#define B2DScale 39.3701
#define NJointsDance 51
#define NFingers 42

//------------Configuration file path--------------
//#define Config "C:\\Users\\student\\Desktop\\Blade2Dance\\config2.txt"

//-----------Joint Names--------
#define Hip "Root"
#define Abdomen "LowerBack"
#define Chest "Thorax"
#define Neck "Neck"
#define Head_comp "Head"
#define Left_Collar "L_Collar"
#define Left_Shoulder "L_Humerus"
#define Left_Forearm "L_Elbow"
#define Left_Hand "L_Wrist"
#define Right_Collar "R_Collar"
#define Right_Shoulder "R_Humerus"
#define Right_Forearm "R_Elbow"
#define Right_Hand "R_Wrist"
#define Left_Thigh "L_Femur"
#define Left_Shin "L_Tibia"
#define Left_Foot "L_Foot"
#define Left_Toe "L_Toe"
#define Right_Thigh "R_Femur"
#define Right_Shin "R_Tibia"
#define Right_Foot "R_Foot"
#define Right_Toe "R_Toe"

using namespace std;

string arrayBlade[DOFBlade] = {""};
string arrayFinger[NFingers] = { ""};

string arrayDOF[6]= {" "}; 
int countDOF;

//---------parameters-------------------
string parse(string line, int parseFlag, string delimiter);
void createNewFile(string BladePath, string BladeError, string DancePath, string DanceError, 
	bool fingerFlag, string fingerDataPath, string fingerDataError);
string convertString(string line);
bool checkLine(string line);

void progress(float progress);

//---------------clase Order-----------------------
class Order{
public:
	string name;
	int blade;
	int nDOF;

	Order();//constructor
	void init(string Joint, int n);
	void initBlade(int n);

};//ordered in Dance order

Order::Order()
{
	name = "blank";
	countDOF = 0;
}
void Order::init(string Joint, int n)
{
	name = Joint;
	nDOF = n;
	blade = -1;
}
void Order::initBlade(int n)
{
	blade = n;
}

//---------class File-------------------
class File{
public:
	ifstream fileStream;
	string path;
	string name;

	File(string filePath, string error);//constructor
	~File();//destructor
	string getLine();


};//class file for organization


File::File(string filePath, string error)
	{
		string temp;
		fileStream.open(filePath.c_str());
		if (fileStream.fail())
		{
			cout << "ERROR: >> " << error<< " path is wrong>>" << flush;
			getchar();
			exit(1);
		}//config file not found
		path = filePath;
		if(filePath.at(0) == '/')
		{
			temp = parse(filePath, 1, "/");
		}
		else
		{
			temp = parse(filePath, 1, "\\");
		}
		name = temp;
		cout<<"Name of " <<error<<" is: " <<name<<endl;
	}//constructor
File::~File()
{
	fileStream.close();
}

string File::getLine()
{
	string line;
	if(getline (fileStream,line))
	{
		return line;
	}
	else
	{
      throw string("getLine()");
  	}
}//get a line from a file


string parse(string line, int parseFlag, string delimiter)
{
	if(!parseFlag)
	{
		return "";
	}//no parsing needed if flag = 0

	size_t pos = 0;
	string token;
	while ((pos = line.find(delimiter)) != string::npos) 
	{
    	token = line.substr(0, pos);
    	line.erase(0, pos + delimiter.length());
    	if(delimiter == " " && parseFlag == 1)
    	{
    		return line;
    	}
    	if(delimiter == " " && parseFlag == 2)
    	{
    		return token;
    	}
    }
    if(parseFlag != 1)
    {
    	return token;
    }//return the token before the parse
    return line;

}//returns string of the path

//-------------------FUNCTIONS---------------------------

void replaceAll(string& line, const string& oldString, const string& newString) 
{
	if(line.find("/", 0) !=string::npos && oldString == "/")
	{
		return;
	}//do nothing for linux paths
    if(oldString.empty())
        return;
    size_t start_pos = 0;
    while((start_pos = line.find(oldString, start_pos)) != string::npos) {
        line.replace(start_pos, oldString.length(), newString);
        start_pos += newString.length(); // In case 'to' contains 'from', like replacing 'x' with 'yx'
    }
}//replaces within the master string an 'old' substring with a 'new' substring


string getFile(){
	OPENFILENAME ofn;
	wchar_t*FilterSpec = L"All Files(.)\0*.*\0";
	wchar_t*Title = L"Choose configuration file....";
	wchar_t szFileName[MAX_PATH];
	wchar_t szFileTitle[MAX_PATH];

	*szFileName = 0; *szFileTitle = 0;

	/* fill in non-variant fields of OPENFILENAME struct. */
	ofn.lStructSize = sizeof(OPENFILENAME);
	ofn.hwndOwner = GetFocus();
	ofn.lpstrFilter = FilterSpec;
	ofn.lpstrCustomFilter = NULL;
	ofn.nMaxCustFilter = 0;
	ofn.nFilterIndex = 0;
	ofn.lpstrFile = szFileName;
	ofn.nMaxFile = MAX_PATH;
	ofn.lpstrInitialDir = L"."; // Initial directory.
	ofn.lpstrFileTitle = szFileTitle;
	ofn.nMaxFileTitle = MAX_PATH;
	ofn.lpstrTitle = Title;
	ofn.lpstrDefExt = 0;

	ofn.Flags = OFN_FILEMUSTEXIST | OFN_HIDEREADONLY;

	if (!GetOpenFileName((LPOPENFILENAME)&ofn))
	{
		return ("NULL"); // Failed or cancelled
	}
	else
	{
		wchar_t *file;
		file = szFileName;
		wstring ws(file);
		string str(ws.begin(), ws.end());
		return str;
	}
}

int main(int argc, char * argv[])
{
	int nFiles;
	string line;
	string BladePath;
	string DancePath;
	string fingerData;
	string BladeError;
	string DanceError;
	string fingerDataError;
	ifstream config;
	bool fingerDataFlag = true;
	//-------------------Open Config file----------------------------
	cout << "Select configuration file to process.."; 
	while(true)
	{
		string configPath= getFile();
		config.open( configPath );
		cout<<endl;
		if (config.fail())
		{
			cout<< endl;
			cout << "ERROR: Configuration file not opened.." << flush;
			getchar();
			exit(1);
		}//config file not found

		//---------------------------------------------------------------

		//-----------------Parsing Config File------------------------

		//Specification information
		getline (config,line);
		if (line != "Blade_2_Dance Converter 2.0")
		{
			cout<<endl;
			cout << "ERROR: Configuration file not correct format.." << endl;
			cout <<endl;
			cout << "Please select another configuration file <<enter>>"<<endl;
			char c = getchar();
			config.close();
			continue;
		}//not a config file
		else
		{
			break;
		}//configuration file is okay

	}//get configuration file loop;

	//Parse number of files
	getline (config,line);
	nFiles = stoi(parse(line, 1, ": "));

	//Parse Dance file path
	getline (config,line);
	DancePath = parse(line, 1, ": ");
	DanceError = parse(line, 2, ": ");
	replaceAll(DancePath, "\\", "\\\\");
	cout<<"Dance file path:"<<DancePath<<endl;

	//-----------------Folder path provided-------------------
	if(nFiles ==0)
	{
		int i = 0;
		DIR *dir;
		struct dirent *ent;
		//Parse Blade folder
		getline (config,line);
		BladePath = parse(line, 1, ": ");
		BladeError = parse(line, 2, ": ");
		replaceAll(BladePath, "\\", "\\\\");
		cout<<"Blade folder path:"<<BladePath<<endl;

		if ((dir = opendir (BladePath.c_str())) != NULL)
		{
			while ((ent = readdir (dir)) != NULL)
			{
				string file = ent->d_name;
				if(file.find(".bvh") != string::npos)
				{
					nFiles++;
				}
			}
			closedir (dir);
		} 
		else 
		{
			cout << "ERROR: Path could not be opened>> " << flush;
			getchar();
			exit(1);
		}

		//fill in data (wont be used)
		getline (config,line);
		fingerData = parse(line, 1, ": ");
		fingerDataError = parse(line, 2, ": ");
		fingerDataError = parse(fingerDataError, 2, "(");
		if(fingerData.find("n/a") != string::npos)
		{
			fingerDataFlag = false;
		}
		
		if ((dir = opendir (BladePath.c_str())) != NULL)
		{
			while ((ent = readdir (dir)) != NULL)
			{
				string file = BladePath + "\\\\" +(ent->d_name);
				if(file.find(".bvh") != string::npos)
				{
					cout<<endl<<"File "<<i+1<<" of "<< nFiles<<"..."<<endl;
					//----------------New File creation-------------------
					createNewFile(file, BladeError, DancePath, DanceError, fingerDataFlag, fingerData, fingerDataError);
					i++;
				}
			}
			closedir (dir);
			cout << endl<< "Done! <<enter>>";
			getchar();
		} 
		else 
		{
			cout << "ERROR: Path could not be opened>> " << flush;
			getchar();
			exit(1);
		}
	}//folder

	else{

	for(int i = 0; i < nFiles; i++){

	//Parse Blade Path
	getline (config,line);
	BladePath = parse(line, 1, ": ");
	BladeError = parse(line, 2, ": ");
	replaceAll(BladePath, "\\", "\\\\");
	cout<<"Blade file path:"<<BladePath<<endl;

	//See if finger motion is present
	getline (config,line);
	fingerData = parse(line, 1, ": ");
	fingerDataError = parse(line, 2, ": ");
	fingerDataError = parse(fingerDataError, 2, "(");
	if(fingerData.find("n/a") != string::npos)
	{
		fingerDataFlag = false;
	}

	cout<<endl<<"File "<<i+1<<" of "<< nFiles<<"..."<<endl;
	//----------------New File creation-------------------
	createNewFile(BladePath, BladeError, DancePath, DanceError, fingerDataFlag, fingerData, fingerDataError);
	}//all the blade files

	cout << endl<< "Done! <<enter>>";
	getchar();
	}//files provided

	return 0;
}

bool checkLine(string line)
{
	if(line.find("MOTION")!=string::npos)
	{
		return true;
	}
	return false;
}
void parseDOF(string line)
{
	size_t pos = 0;
	string token;
	int total =0;
	int count= 0;
	string delimiter = " ";
	while ((pos = line.find(delimiter)) != string::npos) 
	{
    	token = line.substr(0, pos);
    	line.erase(0, pos + delimiter.length());
    	//out<<"token:"<<token<<endl;

    	if(count> 1)
    	{
    		arrayDOF[total] = token;
    		//cout<<"TOKEN" <<total<<":"<<token<<endl;
    		total++;
    	}
    	count++;
    }
    if (!line.empty() && line[line.length()-1] == '\r')
    {
   	 	line.erase(line.length()-1);
	}//remove \n
    arrayDOF[total] = line;
    countDOF = total + 1;
    //cout<<"Count DOF: "<<countDOF;
    /*for(int i = 0; i < countDOF; i++)
    {
    	cout<<"STRING:"<<arrayDOF[i];
    }
    cout<<endl;*/
}

string parseJointLine(string line)
{
	string s1;
	if((line.find("ROOT") != string::npos))
	{
		s1 = parse(line, 1, "ROOT ");
		//s1 = parse(s1, 2, "\r");
	}
	else if((line.find("JOINT") != string::npos))
	{
		s1 =parse(line, 1, "JOINT ");
		//s1 = parse(s1, 2, "\r");
	}

	return s1;
}

void parseMotionLine(string line)
{
	//cout<<"-----------MOTION-----------"<<endl;
	//cout<<line<<endl;
	string word = parse(line, 2, " ");
	line = parse(line, 1, " ");//remove first empty space
	int i;
	for(i  = 0; i < DOFBlade; i++)
	{
		word = parse(line, 2, " ");
		line = parse(line, 1, " ");
		//cout<<"Word:"<<word;
		if(i == DOFBlade-1)
		{
			//cout<<"here"<<line<<endl;
			//line = parse(line, 2, "\r");
			arrayBlade[i] = line;
		}
		else
		{
			arrayBlade[i] = word;
		}
		//cout<<" "<<i<<endl;

	}
	//cout<<"done"<<endl;
}

void parseFinger(string line)
{
	//cout<<"-----------MOTION-----------"<<endl;
	//cout<<line<<endl;
	string word = parse(line, 2, " ");
	//line = parse(line, 1, " ");//remove first empty space
	int k = 0;
	for (int i = 0; i < 92; i++)
	{
		word = parse(line, 2, " ");
		line = parse(line, 1, " ");
		//cout<<"Word:"<<word;
		if ((i >26 && i < 48) || i > 56 && i < 78)
		{
			//line = parse(line, 2, "\r");
			arrayFinger[k] = word;
			k++;
		}
		//cout<<" "<<i<<endl;

	}
	//cout<<"done"<<endl;
}

Order * findOrder(string line, Order *arOrder)
{
	//cout<<"Original Joint:"<<line;
	string newString;
	newString = convertString(line);
	//cout<<" ||New Joint:"<<newString<<endl;
	for(int i = 0; i < NJointsDance; i++ )
    {
    	if((arOrder[i]).name == newString)
		{
			return &(arOrder[i]);
		}
    }
    return NULL;
}

int calculateOffset(int up, Order * arOrder)
{
	int offSet = 0;
	for(int i = 0; i < up; i++)
	{
		for(int j = 0; j < NJointsDance; j++)
		{
			if(arOrder[j].blade == i)
			{
				offSet = offSet + arOrder[j].nDOF;
				break;
			}
		}
	}
	return offSet;
}
void progress(float progress)
{
    int barWidth = 70;

	cout << "[";
    int pos = barWidth * progress;
    for (int i = 0; i < barWidth; ++i) {
        if (i < pos) std::cout << "=";
        else if (i == pos) cout << ">";
        else cout << " ";
    }
    cout << "] " << int(progress * 100.0) << " % \r";
    cout.flush();

}

void createNewFile(string BladePath, string BladeError, string DancePath, string DanceError, 
	bool fingerFlag, string fingerDataPath, string fingerDataError)
{

	int orderCount = 0;
	
	Order *arOrder;
	arOrder = new Order[NJointsDance];

	File blade(BladePath, BladeError);//initialze files
	File dance(DancePath, DanceError);

	string part1 = "Post_B2D_";
	string part2 = blade.name;
	string newFileName = part1+part2;

	ofstream outputFile(newFileName.c_str());

	if (fingerFlag)
	{
		File finger(fingerDataPath, fingerDataError);
		if (!outputFile.is_open())
		{
			cout << "ERROR: Write file could not be opened>> " << flush;
			getchar();
			exit(1);
		}//writing file doesnt open

		//parse finger file-------------
		int totalDOF = 0;
		string temp;
		string jointName = "";
		while (true)
		{
			try
			{
				temp = finger.getLine();
			}
			catch (string &e)
			{
				cerr << "End of Blade file" << endl;
				break;
			}//end of file
			if (checkLine(temp))
			{
				break;
			}//line has motion in it

		}//while you can get strings
		temp = finger.getLine();
		temp = finger.getLine();
		temp = finger.getLine();
		parseFinger(temp);

		while (true)
		{
			try
			{
				temp = dance.getLine();
			}
			catch (string &e)
			{
				cerr << "End of Dance file" << endl;
				break; //or recover from the error
			}//end of file
			if (checkLine(temp))
			{
				outputFile << temp << endl;
				break;
			}//line has Motion in it(end of preamble)

			if ((temp.find("CHANNELS") != string::npos))
			{
				parseDOF(temp);
				string newString = jointName;


				//cout<<countDOF<<endl;

				(arOrder[orderCount]).init(newString, countDOF);
				orderCount++;
				totalDOF = totalDOF + countDOF;

			}//DOF count
			if (temp.find("ROOT") != string::npos || (temp.find("JOINT") != string::npos))
			{
				jointName = parseJointLine(temp);

			}
			outputFile << temp;
			outputFile << "\n";


		}//while you can get strings

		//------------parse Blade file preamble----------

		Order * ptr;

		/*for(int i = 0; i < NJointsDance; i++ )
		{
		cout<< "Name: "<<(arOrder[i]).name << " <<"<<(arOrder[i]).nDOF <<">>"<<endl;
		}//for testing*/

		int bladeCount = 0;
		while (true)
		{
			try
			{
				temp = blade.getLine();
			}
			catch (string &e)
			{
				cerr << "End of Blade file" << endl;
				break;
			}//end of file
			if (checkLine(temp))
			{
				break;
			}//line has motion in it

			if (temp.find("ROOT") != string::npos || (temp.find("JOINT") != string::npos))
			{
				jointName = parseJointLine(temp);
				ptr = findOrder(jointName, arOrder);
				ptr->initBlade(bladeCount);
				bladeCount++;


			}
		}//while you can get strings

		/*for(int i = 0; i < NJointsDance; i++ )
		{

		cout<< "Name: "<<(arOrder[i]).name<<" <<";
		cout<<" "<<(arOrder[i]).blade;
		cout<<endl;
		}//for testing*/


		//Copy the motion data from Blade---------------------------------
		temp = blade.getLine();
		outputFile << temp << endl;
		int frames = stoi(parse(temp, 1, ": "));

		temp = blade.getLine();
		outputFile << temp << endl;
		float progressCount = 0;

		while (true)
		{
			try
			{
				temp = blade.getLine();
			}
			catch (string &e)
			{
				cout << endl;
				cerr << "<<End of Blade file>>" << endl;
				break;
			}//end of file
			parseMotionLine(temp);

			/*for(int k=0; k< DOFBlade; k++){
			cout<<k<<":"<<arrayBlade[k]<<endl;
			}//testing blade array */

			if ((int(progressCount) % 20 == 0) || progressCount + 1 == frames)
			{
				if (progressCount + 1 == frames)
				{
					progress(float(1));
				}
				else
				{
					progress(float(progressCount / frames));
				}
			}//progress bar
			progressCount++;

			int fingerCount = 0;
			for (int n = 0; n < NJointsDance; n++)
			{
				int number = arOrder[n].blade;
				//cout<<number<<endl;
				if (number != -1)
				{
					number = calculateOffset(number, arOrder);
					temp = arrayBlade[number];
					//cout<<"JOINT:"<<arOrder[n].name<<endl;
					for (int j = 0; j < arOrder[n].nDOF; j++)
					{
						if (arOrder[n].nDOF == 6 && j < 3)
						{
							float rand = stof(arrayBlade[number + j]);
							temp = to_string(static_cast<long double>(float(rand) / float(B2DScale)));
							outputFile << temp;
						}//this is the root/hip joint and its the translation data

						else{
							temp = arrayBlade[number + j];
							outputFile << temp;
						}//its a rotational data

						if (n != NJointsDance - 1)
						{
							outputFile << " ";
							//cout<<endl;
						}
					}
				}//data is available
				else
				{
					for (int j = 0; j < arOrder[n].nDOF; j++)
					{
						outputFile << arrayFinger[fingerCount];
						fingerCount++;
						//cout<<"0";
						if (n != NJointsDance - 1)
						{
							outputFile << " ";
							//cout<<endl;
						}
					}
				}//if theres no data

			}//for each data point in Dance
			//cout<<"totalDOF"<<totalDOF<<endl;
			outputFile << endl;
		}//while you can get strings


	}//finger data is available
	else
	{
	 	if (!outputFile.is_open())
	 	{
	 		cout << "ERROR: Write file could not be opened>> " << flush;
			getchar();
			exit(1);
	 	}//file does not open
	 	int totalDOF = 0;
    	string temp;
    	string jointName ="";
	 	//Copy the preamble of Dance file and fill in Order class---------------------
		while(true)
    	{
    		try
    		{
     	 		temp = dance.getLine();
   			}catch(string &e) 
   			{
      			cerr << "End of Dance file"<<endl;
      			break; //or recover from the error
      		}//end of file
    		if(checkLine(temp))
    		{
    			outputFile<<temp<<endl;
    			break;
    		}//line has Motion in it(end of preamble)

    		if((temp.find("CHANNELS") != string::npos))
    		{
	    		parseDOF(temp);
	    		string newString = jointName;


    			//cout<<countDOF<<endl;

    			(arOrder[orderCount]).init(newString, countDOF);
    			orderCount++;
    			totalDOF = totalDOF + countDOF;

	    	}//DOF count
	    	if (temp.find("ROOT") != string::npos || (temp.find("JOINT") != string::npos))
	    	{
    			jointName = parseJointLine(temp);

    		}
    		outputFile<<temp;
			outputFile<<"\n";


    	}//while you can get strings

    	//------------parse Blade file preamble----------

    	Order * ptr;

    	/*for(int i = 0; i < NJointsDance; i++ )
    	{
    		cout<< "Name: "<<(arOrder[i]).name << " <<"<<(arOrder[i]).nDOF <<">>"<<endl;
    	}//for testing*/

    	int bladeCount= 0;
    	while(true)
    	{
    		try
    		{
     	 		temp = blade.getLine();
   			}catch(string &e) 
   			{
      			cerr << "End of Blade file"<<endl;
      			break;
      		}//end of file
    		if(checkLine(temp))
    		{
    			break;
    		}//line has motion in it

    		if (temp.find("ROOT") != string::npos || (temp.find("JOINT") != string::npos))
	    	{
    			jointName = parseJointLine(temp);
    			ptr = findOrder(jointName, arOrder);
    			ptr->initBlade(bladeCount);
    			bladeCount++;
    			

    		}
    	}//while you can get strings

    	/*for(int i = 0; i < NJointsDance; i++ )
    	{

    		cout<< "Name: "<<(arOrder[i]).name<<" <<";
    		cout<<" "<<(arOrder[i]).blade;
    		cout<<endl;
    	}//for testing*/


    	//Copy the motion data from Blade---------------------------------
    	temp = blade.getLine();
    	outputFile<<temp<<endl;
    	int frames = stoi(parse(temp, 1, ": "));

    	temp = blade.getLine();
    	outputFile<<temp<<endl;
    	float progressCount = 0;

		while(true)
    	{
    		try
    		{
     	 		temp = blade.getLine();
   			}catch(string &e) 
   			{
   				cout<<endl;
      			cerr << "<<End of Blade file>>"<<endl;
      			break;
      		}//end of file
      		parseMotionLine(temp);

			/*for(int k=0; k< DOFBlade; k++){
				cout<<k<<":"<<arrayBlade[k]<<endl;
			}//testing blade array */

      		if((int(progressCount)%20 == 0) || progressCount+1 == frames)
      		{
      			if(progressCount+1 == frames)
      			{
      				progress(float(1));
      			}
      			else
      			{
      				progress(float(progressCount/frames));
      			}
      		}//progress bar
      		progressCount++;


      		for(int n = 0; n < NJointsDance; n++)
      		{	
      			int number = arOrder[n].blade;
      			//cout<<number<<endl;
      			if(number != -1)
      			{
       				number = calculateOffset(number, arOrder);
      				temp = arrayBlade[number];
      				//cout<<"JOINT:"<<arOrder[n].name<<endl;
      				for(int j = 0; j < arOrder[n].nDOF; j++)
      				{
						if(arOrder[n].nDOF == 6 && j < 3)
						{
							float rand= stof(arrayBlade[number+j]);
							temp = to_string(static_cast<long double>(float(rand)/float(B2DScale)));
							outputFile<<temp;
						}//this is the root/hip joint and its the translation data

						else{
      					temp = arrayBlade[number+j];
      					outputFile<<temp;
						}//its a rotational data

      					if(n!= NJointsDance-1)
      					{
      						outputFile<<" ";
      						//cout<<endl;
      					}
      				}
      			}//data is available
      			else
      			{
      				for(int j = 0; j < arOrder[n].nDOF; j++)
      				{
      					outputFile<<"0";
      					//cout<<"0";
      					if(n!= NJointsDance-1)
      					{
      						outputFile<<" ";
      						//cout<<endl;
      					}
      				}
      			}//if theres no data

      		}//for each data point in Dance
      		//cout<<"totalDOF"<<totalDOF<<endl;
      		outputFile<<endl;
    	}//while you can get strings


	}//finger data is is not available
	outputFile.close();
	cout<<"OutputFile:<<"<<newFileName<<">>"<<endl;
	//cout << "Done! <<enter>>";
	//getchar();
	

	delete[] arOrder;

	return;
}

string convertString(string line)
{
	if(line == Hip)
	{
		line = "Hip";
	}
	if(line == Abdomen)
	{
		line = "Abdomen";
	}
	if(line == Chest)
	{
		line = "Chest";
	}
	if(line == Neck)
	{
		line = "Neck";
	}
	if(line == Head_comp)
	{
		line = "Head_comp";
	}
	//------------------HAND-----------
	if(line == Left_Collar)
	{
		line = "Left_Collar";
	}
	if(line == Left_Shoulder)
	{
		line = "Left_Shoulder";
	}
	if(line == Left_Forearm)
	{
		line = "Left_Forearm";
	}
	if(line == Left_Hand)
	{
		line = "Left_Hand";
	}
	if(line == Right_Collar)
	{
		line = "Right_Collar";
	}
	if(line == Right_Shoulder)
	{
		line = "Right_Shoulder";
	}
	if(line == Right_Forearm)
	{
		line = "Right_Forearm";
	}
	if(line == Right_Hand)
	{
		line = "Right_Hand";
	}
	//--------------------Legs------------
	if(line == Left_Thigh)
	{
		line = "Left_Thigh";
	}
	if(line == Left_Shin)
	{
		line = "Left_Shin";
	}
	if(line == Left_Foot)
	{
		line = "Left_Foot";
	}
	if(line == Left_Toe)
	{
		line = "Left_Toe";
	}
	if(line == Right_Thigh)
	{
		line = "Right_Thigh";
	}
	if(line == Right_Shin)
	{
		line = "Right_Shin";
	}
	if(line == Right_Foot)
	{
		line = "Right_Foot";
	}
	if(line == Right_Toe)
	{
		line = "Right_Toe";
	}
	return line;
}//returns Blade corresponding Dance joint
