import CoreWLAN
import Foundation

struct NetworkInfo: Codable {
    let ssid: String
    let rssi: Int
    let security: String
    let channel: Int
    let band: String
}

func getSecurityString(_ network: CWNetwork) -> String {
    if network.supportsSecurity(.wpa3Personal) { return "WPA3 Personal" }
    if network.supportsSecurity(.wpa3Enterprise) { return "WPA3 Enterprise" }
    if network.supportsSecurity(.wpa2Personal) { return "WPA2 Personal" }
    if network.supportsSecurity(.wpa2Enterprise) { return "WPA2 Enterprise" }
    if network.supportsSecurity(.wpaPersonal) { return "WPA Personal" }
    if network.supportsSecurity(.wpaEnterprise) { return "WPA Enterprise" }
    if network.supportsSecurity(.dynamicWEP) { return "WEP" }
    return "None"
}

func getBandString(_ channel: CWChannel?) -> String {
    guard let ch = channel else { return "Unknown" }
    switch ch.channelBand {
    case .band2GHz: return "2.4 GHz"
    case .band5GHz: return "5 GHz"
    case .band6GHz: return "6 GHz"
    default: return "Unknown"
    }
}

guard let interface = CWWiFiClient.shared().interface() else {
    print("Error: Could not find any WiFi interfaces.")
    exit(1)
}

do {
    let networks = try interface.scanForNetworks(withName: nil)
    var results: [NetworkInfo] = []
    
    for network in networks {
        // If SSID is nil, it usually means location permissions are missing
        let ssid = network.ssid ?? "[Redacted/Hidden]"
        
        results.append(NetworkInfo(
            ssid: ssid,
            rssi: network.rssiValue,
            security: getSecurityString(network),
            channel: Int(network.wlanChannel?.channelNumber ?? 0),
            band: getBandString(network.wlanChannel)
        ))
    }
    
    let encoder = JSONEncoder()
    encoder.outputFormatting = .prettyPrinted
    if let data = try? encoder.encode(results),
       let jsonString = String(data: data, encoding: .utf8) {
        print(jsonString)
    }
} catch {
    print("Error during scan: \(error.localizedDescription)")
    exit(1)
}
