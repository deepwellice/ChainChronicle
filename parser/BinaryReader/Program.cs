using System.Text;
using System.Text.RegularExpressions;
using System.IO;
using Ionic.Zlib;
using System.Windows.Forms;

namespace BinaryReader
{
    class Program
    {
        public static void DecodeXorData(ref byte[] from)
        {
            if (from.Length <= 8)
            {
                return;
            }
            byte[] key = new byte[11];
            key[0] = 0x55;
            key[1] = 0x6E;
            key[2] = 0x69;
            key[3] = 0x74;
            key[4] = 0x79;
            key[5] = 0x57;
            key[6] = 0x65;
            key[7] = 0x62;
            key[8] = 0x00;
            key[9] = 0x00;
            key[10] = 0x00;
            for (int i = 0; i < key.Length; i++)
            {
                key[i] ^= from[i];
            }
            int len = from.Length;
            if (len > 256)
                len = 256;
            for (int i = 0; i < len; i++)
            {
                from[i] ^= key[i % 11];
            }
        }

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

        static void decode_BGM()
        {
            string bgm_path = "E:\\CodeDepot\\Github\\ChainChronicle\\data\\packed\\jp\\BGM_SAKURA_002.bdl";
            string bgm_path_decode = "E:\\CodeDepot\\Github\\ChainChronicle\\data\\packed\\jp\\BGM_SAKURA_002.assets";
            byte[] bgm_data = File.ReadAllBytes(bgm_path);
            DecodeXorData(ref bgm_data);
            FileStream fout = File.Create(bgm_path_decode);
            fout.Write(bgm_data, 0, bgm_data.Length);
        }

        static void Main(string[] args)
        {
            convert_json();
            //decode_BGM();
        }
    }
}
