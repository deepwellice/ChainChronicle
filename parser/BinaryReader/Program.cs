using System.Text;
using System.Text.RegularExpressions;
using System.IO;
using Ionic.Zlib;
using System.Windows.Forms;

namespace BinaryReader
{
    class Program
    {
        //static string dataPath = "E:\\CodeDepot\\ChainChronicle\\ccdatareader\\data\\jp";
        //static string extactDataPath = "E:\\CodeDepot\\ChainChronicle\\ccdatareader\\extracteddata";
        static string strBinaryDataFolder;
        static string strUnpackedDataFolder;

        static string GetBinaryDataFolder()
        {
            if (!Directory.Exists(strBinaryDataFolder))
            {
                string strExePath = Application.ExecutablePath;
                int foundIndex = strExePath.IndexOf("\\parser\\");
                if (foundIndex < 0)
                {
                    MessageBox.Show("cannot find data files.");
                    return "";
                }
                strBinaryDataFolder = strExePath.Remove(foundIndex) + ("\\data\\packed\\jp");
            }
            
            return strBinaryDataFolder;
        }
        static string GetUnpackedDataFolder()
        {
            if (!Directory.Exists(strUnpackedDataFolder))
            {
                string strExePath = Application.ExecutablePath;
                int foundIndex = strExePath.IndexOf("\\parser\\");
                strUnpackedDataFolder = strExePath.Remove(foundIndex) + ("\\data\\unpacked\\jp");
            }
            
            return strUnpackedDataFolder;
        }

        static void convert_json()
        {
            string strBinDataFolder = GetBinaryDataFolder();
            if (!Directory.Exists(strBinaryDataFolder))
                return;
            string strUnpackedDataFolder = GetUnpackedDataFolder();
            if (!Directory.Exists(strUnpackedDataFolder))
                Directory.CreateDirectory(strUnpackedDataFolder);
            DirectoryInfo dataDirInfo = new DirectoryInfo(strBinDataFolder);
            FileInfo[] files = dataDirInfo.GetFiles();
            foreach (FileInfo fi in files)
            {
                string fullName = fi.FullName;
                if (fi.Extension != ".data5_1")
                    continue;
                int dotPos = fullName.LastIndexOf('.');
                string newFullName = fullName.Remove(dotPos, fullName.Length - dotPos);
                int slashPos = fullName.LastIndexOf('\\');
                newFullName = newFullName.Substring(slashPos + 1);
                newFullName = strUnpackedDataFolder + '\\' + newFullName + "_jp.json";
                byte[] compressed = File.ReadAllBytes(fullName);
                string json = GZipStream.UncompressString(compressed);
                json = Regex.Unescape(json);
                json = json.Replace("\t", "");
                json = json.Replace("\n", "");
                FileStream fout = File.Create(newFullName);
                byte[] jsonBytes = Encoding.UTF8.GetBytes(json);
                fout.Write(jsonBytes, 0, jsonBytes.Length);
                fout.Close();
            }
        }

        static void convert_charainfo_data()
        {
            string charainfoDataFilePath = strUnpackedDataFolder + "\\charainfo_jp.json";

        }

        static void Main(string[] args)
        {
            convert_json();
            convert_charainfo_data();
        }
    }
}
